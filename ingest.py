import fitz  # PyMuPDF
import json
import os
import re
import pickle
from rank_bm25 import BM25Okapi

def process_amm_pdf(pdf_path, data_dir):
    print(f"Starting ingestion for {pdf_path}...")
    doc = fitz.open(pdf_path)
    
    chunks = []
    corpus = [] # For BM25
    
    schematics_dir = os.path.join(data_dir, "schematics")
    os.makedirs(schematics_dir, exist_ok=True)
    
    # Pattern to find ATA chapter in footer (e.g. 72-00-00, 72-21-03)
    ata_pattern = re.compile(r'(\d{2}[-\u00ad]\d{2}[-\u00ad]\d{2})')
    
    print(f"Processing {len(doc)} pages...")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # 1. Extract ATA Chapter from the bottom of the page (footer)
        ata_chapter = "Unknown"
        # Look for the pattern in the last 500 characters which usually contains the footer
        footer_text = text[-500:] if len(text) > 500 else text
        matches = ata_pattern.findall(footer_text)
        if matches:
            # Take the last match which is usually the actual chapter number, normalize hyphens
            ata_chapter = matches[-1].replace('\u00ad', '-')
            
        # 2. Extract Figures
        figure_ids = []
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Get dimensions
            img_width = base_image.get("width", 0)
            img_height = base_image.get("height", 0)
            
            # Filter out tiny images (e.g. logos, icons, noise)
            if img_width >= 100 and img_height >= 100:
                fig_id = f"{page_num + 1}_{img_index}"
                figure_ids.append(fig_id)
                
                # Save image
                img_filename = f"{fig_id}.{image_ext}"
                img_path = os.path.join(schematics_dir, img_filename)
                
                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)
        
        # 3. Create Chunk
        page_no = page_num + 1
        chunk_id = f"chunk_p{page_no}"
        
        chunk = {
            "chunk_id": chunk_id,
            "page_no": page_no,
            "ata_chapter": ata_chapter,
            "content": text,
            "figure_ids": figure_ids
        }
        chunks.append(chunk)
        
        # 4. Tokenize for BM25
        tokenized_text = text.lower().split()
        corpus.append(tokenized_text)
        
        if (page_num + 1) % 100 == 0:
            print(f"Processed {page_num + 1} pages...")
            
    # 5. Build and Serialize BM25 Index
    print("Building BM25 Index...")
    bm25 = BM25Okapi(corpus)
    
    bm25_path = os.path.join(data_dir, "bm25_index.pkl")
    print(f"Serializing BM25 index to {bm25_path}...")
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25, f)
        
    # 6. Save JSON Data
    json_path = os.path.join(data_dir, "amm_chunks.json")
    print(f"Saving chunk data to {json_path}...")
    with open(json_path, "w") as f:
        json.dump(chunks, f, indent=2)
        
    print("Ingestion complete!")

if __name__ == "__main__":
    pdf_file = "72_G__027.pdf"
    output_dir = "AMM_MVP_Data"
    
    if not os.path.exists(pdf_file):
        print(f"Error: {pdf_file} not found!")
    else:
        process_amm_pdf(pdf_file, output_dir)
