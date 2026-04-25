import json
from rank_bm25 import BM25Okapi

# 1. Load your extracted data
with open("amm_text_index.json", "r") as f:
    pages = json.load(f)

# 2. Tokenize for BM25
corpus = [p['content'].lower().split() for p in pages]
bm25 = BM25Okapi(corpus)

def search_manual(query):
    tokenized_query = query.lower().split()
    # Get top 3 matching pages
    results = bm25.get_top_n(tokenized_query, pages, n=3)
    
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} (Page {res['page']}) ---")
        print(res['content'][:500] + "...") # Show snippet

# Try it out:
search_manual("area F Figure 601 (Sheet 3)")