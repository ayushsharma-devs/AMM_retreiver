#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
pip install gdown

# Run a small python script to grab the data
python -m gdown --id 1MGjbBRh0Lk2T5EjpoU-18ajLVWEprX8a -o amm_index.json
python -m gdown --id 1XTAhvwJWyfRs84F_WZahDIwgmUXiPhAV -o bm25.pkl