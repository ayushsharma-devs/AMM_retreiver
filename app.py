import streamlit as st
import json
from rank_bm25 import BM25Okapi
import fitz  # To show the actual PDF page

# Page Config
st.set_page_config(page_title="AMM Retriever MVP", layout="wide")
st.title("✈️ Aircraft Maintenance Manual Search")
st.write("Verbatim Retrieval for 737 MAX Field Testing")

# 1. Load Data
@st.cache_data
def load_data():
    with open("amm_text_index.json", "r") as f:
        data = json.load(f)
    corpus = [p['content'].lower().split() for p in data]
    return data, BM25Okapi(corpus)

pages, bm25 = load_data()

# 2. Search Input
query = st.text_input("Enter damage description (e.g., 'dent leading edge station 2')", "")

if query:
    tokenized_query = query.lower().split()
    results = bm25.get_top_n(tokenized_query, pages, n=5)

    st.subheader(f"Top {len(results)} Verbatim Matches:")
    
    for i, res in enumerate(results):
        with st.expander(f"Match {i+1}: Page {res['page']}", expanded=(i==0)):
            # Show the text
            st.code(res['content'], language="text")
            
            # Button to 'verify' in original PDF
            st.info(f"👉 Please verify this on Page {res['page']} of the original AMM PDF.")

# Sidebar for Instructions
st.sidebar.header("Field Test Instructions")
st.sidebar.write("""
1. Enter keywords like 'dent', 'scratch', or 'station'.
2. Review the verbatim text in the boxes.
3. Open the PDF to the matching page to see schematics.
""")