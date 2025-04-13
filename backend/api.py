from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
import uuid
from code_analyzer.pipeline import analyze_code
import os
from datetime import datetime
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
import logging

app = FastAPI(
    title="AI Code Analysis API",
    description="API for AI-based code analysis and correctness assessment",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_WINDOW = 100  # Increased from 10 to 100 requests per minute
request_times = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Store analysis results and status
analysis_results = {}
analysis_status = {}
analysis_timestamps = {}

class CodeSubmission(BaseModel):
    code: str = Field(..., min_length=1, description="The code to analyze")
    language: str = Field(default="python", description="Programming language of the code")
    mode: str = Field(default="full", description="Analysis mode: 'full', 'quick', or 'deep'")

async def get_api_key(api_key: str = Depends(api_key_header)):
    # In production, validate against a database or environment variable
    if api_key != os.getenv("API_KEY", "test_key"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = datetime.now()
    
    if client_ip in request_times:
        # Remove old timestamps
        request_times[client_ip] = [t for t in request_times[client_ip] 
                                  if (current_time - t).total_seconds() < RATE_LIMIT_WINDOW]
        
        if len(request_times[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again in a minute."}
            )
        
        request_times[client_ip].append(current_time)
    else:
        request_times[client_ip] = [current_time]
    
    response = await call_next(request)
    return response

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def submit_code(
    code_submission: CodeSubmission,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    logger.info("Received code analysis request")
    analysis_id = str(uuid.uuid4())
    analysis_status[analysis_id] = "processing"
    analysis_timestamps[analysis_id] = datetime.now()
    
    # Process the code directly without creating a temporary file
    background_tasks.add_task(
        run_analysis_direct, 
        analysis_id, 
        code_submission.code,
        code_submission.mode,
        code_submission.language
    )
    
    return {
        "analysis_id": analysis_id,
        "status": "processing",
        "message": "Analysis started"
    }


# New method that processes code strings directly
async def run_analysis_direct(analysis_id: str, code_string: str, mode: str, language: str = 'python'):
    try:
        logger.info(f"Starting direct analysis for ID: {analysis_id} with language: {language}")
        
        # Process the code string directly with language parameter
        results = analyze_code(code_string, mode=mode, is_code_string=True, language=language)
        
        if 'error' in results:
            logger.error(f"Analysis {analysis_id} failed: {results['error']}")
            analysis_status[analysis_id] = "failed"
            analysis_results[analysis_id] = {"error": results['error']}
        else:
            # Save the results
            analysis_results[analysis_id] = results
            analysis_status[analysis_id] = "completed"
            logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed with exception: {str(e)}")
        analysis_status[analysis_id] = "failed"
        analysis_results[analysis_id] = {"error": str(e)}

@app.get("/status/{analysis_id}")
async def get_status(
    analysis_id: str,
    api_key: str = Depends(get_api_key)
):
    logger.info(f"Status check for analysis: {analysis_id}")
    
    if analysis_id not in analysis_status:
        logger.error(f"Analysis ID not found: {analysis_id}")
        raise HTTPException(status_code=404, detail="Analysis ID not found")
    
    # Get current step based on analysis status
    current_step = "submitting"
    if analysis_status[analysis_id] == "processing":
        # Check which sections have been completed
        if analysis_id in analysis_results:
            results = analysis_results[analysis_id]
            if "correctness_analysis" in results and results["correctness_analysis"]:
                current_step = "correctness"
            elif "edge_cases" in results and results["edge_cases"]:
                current_step = "edge_cases"
            elif "semantic_analysis" in results and results["semantic_analysis"]:
                current_step = "semantic"
            elif "test_cases" in results and results["test_cases"]:
                current_step = "test_cases"
    elif analysis_status[analysis_id] == "completed":
        current_step = "completed"
    
    # Return detailed status
    logger.info(f"Current step for {analysis_id}: {current_step}")
    
    return {
        "status": analysis_status[analysis_id],
        "current_step": current_step,
        "progress": get_progress_percentage(current_step),
        "submitted_at": analysis_timestamps[analysis_id].isoformat() if analysis_id in analysis_timestamps else None
    }

def get_progress_percentage(current_step: str) -> int:
    steps = ["submitting", "correctness", "edge_cases", "semantic", "test_cases"]
    current_index = steps.index(current_step)
    return int((current_index / (len(steps) - 1)) * 100)

@app.get("/results/{analysis_id}")
async def get_results(
    analysis_id: str,
    api_key: str = Depends(get_api_key)
):
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")
    if analysis_status[analysis_id] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    return {
        "analysis_id": analysis_id,
        "results": analysis_results[analysis_id],
        "completed_at": datetime.now().isoformat()
    }


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Code Analysis API",
        version="1.0.0",
        description="API for AI-based code analysis and correctness assessment",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Add security requirements
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

