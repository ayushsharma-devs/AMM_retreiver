import os
import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.search_engine import SearchEngine
from dotenv import load_dotenv
import api.audit_db as audit_db

# Load environment variables from .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Initialize app
app = FastAPI(title="AMM Retriever API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
# Placeholder for Next.js frontend URL
ALLOWED_ORIGINS = ["http://localhost:3000", "https://your-vercel-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Search Engine
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AMM_MVP_Data")
search_engine = SearchEngine(DATA_DIR)

# Database Setup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Audit DB...")
    audit_db.init_db()
    
    logger.info("Starting background data loading...")
    asyncio.create_task(load_data_with_retry())

async def load_data_with_retry(max_retries=3):
    retry_count = 0
    base_delay = 2 # seconds
    
    while retry_count < max_retries:
        logger.info(f"Attempting to load data (Attempt {retry_count + 1}/{max_retries})...")
        success = search_engine.load_data()
        
        if success:
            logger.info("Data loaded successfully!")
            return
            
        retry_count += 1
        delay = base_delay ** retry_count
        logger.warning(f"Failed to load data. Retrying in {delay} seconds...")
        await asyncio.sleep(delay)
        
    logger.error("Failed to load data after maximum retries.")

# Models
class AuditRequest(BaseModel):
    user_agent: str

# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "search_engine_ready": search_engine.is_ready,
        "chunks_loaded": len(search_engine.chunks) if search_engine.is_ready else 0
    }

@app.get("/search")
@limiter.limit("20/minute")
async def search(request: Request, q: str, ata: Optional[str] = None):
    if not search_engine.is_ready:
        raise HTTPException(status_code=503, detail="Search engine is still initializing. Please try again later.")
        
    results = search_engine.search(query=q, ata_filter=ata)
    return {"results": results}

@app.get("/figure/{page_no}/{fig_index}")
async def get_figure(page_no: int, fig_index: int):
    fig_id = f"{page_no}_{fig_index}"
    # Using wildcard for extension for simplicity, though we could specify
    schematics_dir = os.path.join(DATA_DIR, "schematics")
    
    # Search for any image with this id
    for filename in os.listdir(schematics_dir):
        if filename.startswith(fig_id + "."):
            filepath = os.path.join(schematics_dir, filename)
            return FileResponse(filepath)
            
    raise HTTPException(status_code=404, detail="Figure not found")

@app.post("/audit/accept")
async def accept_disclaimer(request: Request, audit_data: AuditRequest):
    ip = get_remote_address(request)
    try:
        audit_db.log_acceptance(ip_address=ip, user_agent=audit_data.user_agent)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error logging acceptance: {e}")
        raise HTTPException(status_code=500, detail="Failed to log acceptance")
