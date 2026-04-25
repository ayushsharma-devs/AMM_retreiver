import streamlit as st
import json
from rank_bm25 import BM25Okapi
import requests # Critical missing import
import base64
import gdown
import os
# Page Config
st.set_page_config(page_title="AMM Retriever MVP", layout="wide")
st.title("✈️ Aircraft Maintenance Manual Search")
st.write("Verbatim Retrieval for 737 MAX Field Testing")

# Simple password protection
pwd_input = st.text_input("Enter Access Code", type="password")

if not pwd_input:
    st.info("Please enter the access code to proceed.")
    st.stop()

if pwd_input != st.secrets["ACCESS_PASSWORD"]:
    st.error("❌ Incorrect password. Please try again.")
    st.stop()

st.success("✅ Access granted!")

# 1. Load Data

@st.cache_data
def load_data():
    # Use the ID instead of a messy URL
    file_id = st.secrets["JSON_ID"]
    url = f'https://drive.google.com/uc?id={file_id}'
    output = "temp_index.json"
    
    if not os.path.exists(output):
        # fuzzy=True helps gdown find the ID even if the URL is weird
        path = gdown.download(url, output, quiet=False, fuzzy=True)
        if path is None:
            st.error("Failed to download the index. Check the File ID and Permissions.")
            st.stop()
    
    with open(output, "r") as f:
        data = json.load(f)
        
    corpus = [p['content'].lower().split() for p in data]
    return data, BM25Okapi(corpus)

pages, bm25 = load_data()

# Helper to get PDF (either local or from cloud)
@st.cache_data
def get_pdf_bytes():
    # Try local first (for your laptop test)
    try:
        with open("72_G__027.pdf", "rb") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to Cloud Secret URL
        response = requests.get(st.secrets["PDF_URL"])
        return response.content

# 2. Search Input
query = st.text_input("Enter damage description (e.g., 'dent leading edge station 2')", "")

if query:
    tokenized_query = query.lower().split()
    results = bm25.get_top_n(tokenized_query, pages, n=5)

    st.subheader(f"Top {len(results)} Verbatim Matches:")
    
    pdf_bytes = get_pdf_bytes() # Fetch PDF data once per search

    for i, res in enumerate(results):
        with st.expander(f"Match {i+1}: Page {res['page']}", expanded=(i==0)):
            st.code(res['content'], language="text")
            st.info(f"👉 Please verify this on Page {res['page']} of the original AMM PDF.")

            st.download_button(
                label=f"📥 Download Manual to view Page {res['page']}",
                data=pdf_bytes,
                file_name="737_MAX_AMM.pdf",
                mime="application/pdf",
                key=f"download_btn_{i}"
            )

# Sidebar
st.sidebar.header("Field Test Instructions")
st.sidebar.write("1. Enter keywords. \n2. Review text. \n3. Use the PDF to see schematics.")