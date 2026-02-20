from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from app.utils.resume_generator import ResumeGenerator
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    tags=["builder"]
)

class ExperienceItem(BaseModel):
    title: str
    company: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    description: Optional[str] = None

class EducationItem(BaseModel):
    school: str
    degree: Optional[str] = None
    year: Optional[str] = None

class ProjectItem(BaseModel):
    name: str
    description: Optional[str] = None

class ResumeData(BaseModel):
    fullName: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    skills: Optional[str] = None
    projects: List[ProjectItem] = []

@router.post("/generate")
async def generate_resume(data: ResumeData):
    try:
        generator = ResumeGenerator()
        pdf_buffer = generator.generate(data.dict())
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={data.fullName.replace(' ', '_')}_Resume.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
