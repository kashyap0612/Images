from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.auth import get_current_user
from app.database import get_supabase_client
from app.pipeline.runner import run_scraping_pipeline

app = FastAPI(title="AutoDataset API", version="1.0.0")

# Setup CORS for local React integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobCreate(BaseModel):
    query: str

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AutoDataset"}

@app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """
    Submits a search query, creates a job record in Supabase DB,
    and runs the web scraping and classification tasks in the background.
    """
    query_str = payload.query.strip()
    if not query_str:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    supabase = get_supabase_client()
    try:
        # 1. Register job in database
        job_data = {
            "user_id": user.id,
            "query": query_str,
            "status": "pending",
            "progress": 0,
            "total_images": 0
        }
        res = supabase.table("jobs").insert(job_data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create job row")
            
        job_record = res.data[0]
        job_id = job_record["id"]
        
        # 2. Hand-off execution to background worker thread
        background_tasks.add_task(run_scraping_pipeline, job_id, query_str)
        
        return {
            "message": "Scraper task initialized",
            "job": job_record
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit background task: {str(e)}"
        )

@app.get("/api/jobs")
def list_jobs(user=Depends(get_current_user)):
    """Retrieves all previous runs triggered by the current user."""
    supabase = get_supabase_client()
    try:
        res = supabase.table("jobs").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
def get_job_details(job_id: str, user=Depends(get_current_user)):
    """Retrieves the status, progress, and classified images for a specific job."""
    supabase = get_supabase_client()
    try:
        # Fetch job info
        job_res = supabase.table("jobs").select("*").eq("id", job_id).execute()
        if not job_res.data:
            raise HTTPException(status_code=404, detail="Job record not found")
            
        job = job_res.data[0]
        
        # Security check: verify this belongs to the logged-in user
        if job["user_id"] != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this resource"
            )
            
        # Fetch matching images
        images_res = supabase.table("dataset_images").select("*").eq("job_id", job_id).execute()
        
        return {
            "job": job,
            "images": images_res.data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
