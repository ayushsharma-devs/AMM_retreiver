import json
import pickle
import os
import gdown
from typing import List, Dict, Any

class SearchEngine:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks = []
        self.bm25 = None
        self.is_ready = False
        
    def load_data(self) -> bool:
        """Loads chunks and BM25 index. Returns True if successful."""
        chunks_path = os.path.join(self.data_dir, "amm_chunks.json")
        bm25_path = os.path.join(self.data_dir, "bm25_index.pkl")
        
        try:
            with open(chunks_path, "r") as f:
                self.chunks = json.load(f)
                
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
                
            if len(self.chunks) > 0 and self.bm25 is not None:
                self.is_ready = True
                return True
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def search(self, query: str, ata_filter: str = None, top_n: int = 5) -> List[Dict[str, Any]]:
        if not self.is_ready:
            return []
            
        tokenized_query = query.lower().split()
        
        # Get scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair up scores with chunks
        scored_chunks = list(zip(scores, self.chunks))
        
        # Filter by ATA chapter if provided
        if ata_filter:
            scored_chunks = [sc for sc in scored_chunks if sc[1]["ata_chapter"] == ata_filter]
            
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Return top N chunks, including the score
        results = []
        for score, chunk in scored_chunks[:top_n]:
            if score > 0: # Only return matches
                res = chunk.copy()
                res["score"] = score
                results.append(res)
                
        return results
