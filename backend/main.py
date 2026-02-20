from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load .env from root directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))

# Add backend directory to sys.path so 'app' module can be found
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routers import resume, jobs, feedback, builder

app = FastAPI(title="Smart Resume AI API")

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Resume AI API"}

# Include Routers
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(builder.router, prefix="/api/builder", tags=["builder"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
