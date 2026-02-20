from fastapi import APIRouter, Query
from app.jobs.job_portals import JobPortal

router = APIRouter()

@router.get("/search")
def search_jobs(
    title: str,
    location: str,
    experience: str = Query("all")
):
    portal = JobPortal()
    # JobPortal expects experience as a dict with 'id' key
    exp_dict = {"id": experience, "text": experience}
    results = portal.search_jobs(title, location, exp_dict)
    return results
