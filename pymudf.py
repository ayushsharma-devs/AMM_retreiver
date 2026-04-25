import fitz  # PyMuPDF
import json
import os

def fast_extract(pdf_path, output_json):
    doc = fitz.open(pdf_path)
    data = []

    print(f"Extracting {len(doc)} pages...")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text") # Simple text extraction
        
        # Store page and text for the search index
        data.append({
            "page": page_num + 1,
            "content": text
        })
        
        if page_num % 100 == 0:
            print(f"Processed {page_num} pages...")

    with open(output_json, "w") as f:
        json.dump(data, f)
    print("Done! All pages extracted to JSON.")

if __name__ == "__main__":
    fast_extract("72_G__027.pdf", "AMM_MVP_Data\amm_text_index.json")