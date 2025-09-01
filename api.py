# api.py - FastAPI backend for the Telegram Mini App
import logging
import sys
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intelligence.analysis import get_ai_analysis
from calc.profile import calculate_core_profile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Numbers Bot AI API", version="1.0.0")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ProfileRequest(BaseModel):
    profile: Dict[str, Any]

class AnalysisResponse(BaseModel):
    analysis: str

class CalculationRequest(BaseModel):
    name: str
    birthdate: str

class CalculationResponse(BaseModel):
    profile: Dict[str, Any]

# API endpoints
@app.post("/api/ai/analysis", response_model=AnalysisResponse)
async def get_ai_analysis_endpoint(request: ProfileRequest):
    """Get AI analysis for a core profile."""
    try:
        logger.info(f"Received AI analysis request for profile: {request.profile}")
        
        # Call the existing Python AI analysis function
        analysis = await get_ai_analysis(request.profile)
        
        logger.info("AI analysis completed successfully")
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.post("/api/calculate/core", response_model=CalculationResponse)
async def calculate_core_profile_endpoint(request: CalculationRequest):
    """Calculate core profile for name and birthdate."""
    try:
        logger.info(f"Received calculation request for name: {request.name}, birthdate: {request.birthdate}")
        
        # Call the existing Python calculation function
        profile = calculate_core_profile(request.name, request.birthdate)
        
        logger.info("Core profile calculation completed successfully")
        return CalculationResponse(profile=profile)
    except Exception as e:
        logger.error(f"Core profile calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Core profile calculation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Check if a port was provided as a command line argument
    port = 8000  # default port
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                logger.error("Invalid port number provided")
                sys.exit(1)
    
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)