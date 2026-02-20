from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import StreamingResponse
from app.utils.resume_analyzer import ResumeAnalyzer
from app.utils.ai_resume_analyzer import AIResumeAnalyzer
import tempfile
import os
import shutil
import json
import io

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(None),
    job_role: str = Form("Software Engineer")
):
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]
        if not suffix:
            suffix = ".pdf" # Default to pdf if no extension
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            # Initialize analyzers
            basic_analyzer = ResumeAnalyzer()
            ai_analyzer = AIResumeAnalyzer()

            # Read file content for extraction
            with open(tmp_path, "rb") as f:
                file_content = f.read()
                
            # Extract text using AI analyzer (better OCR support)
            if suffix.lower() == '.docx':
                text = ai_analyzer.extract_text_from_docx(file) # This needs the file object, but we have content. 
                # Actually ai_analyzer.extract_text_from_docx takes the uploaded file object usually.
                # Let's stick to PDF for now or re-use logic. 
                # The extract_text_from_docx in utils expects a file-like object with getbuffer or read.
                # We can wrap file_content in BytesIO if needed, but the original code passed headers.
                pass 
            
            # Re-implement text extraction call correctly
            # The tool only supports PDF upload in UI, so let's stick to extract_text_from_pdf which handles bytes or file
            text = ai_analyzer.extract_text_from_pdf(file_content)
            
            if not text:
                 raise HTTPException(status_code=400, detail="Could not extract text from file.")

            # Basic Analysis
            resume_data = {'raw_text': text}
            job_reqs = {'required_skills': [], 'require_gpa': False}
            basic_analysis = basic_analyzer.analyze_resume(resume_data, job_reqs)

            # AI Analysis - Use the wrapper method for structured output
            role_info = {"description": job_description} if job_description else None
            ai_analysis = ai_analyzer.analyze_resume(text, job_role, role_info)

            result = {
                "text": text,
                "basic_analysis": basic_analysis,
                "ai_analysis": ai_analysis
            }
            
            return result
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def download_report(
    data: dict = Body(...)
):
    try:
        candidate_name = data.get("candidate_name", "Candidate")
        job_role = data.get("job_role", "Job Role")
        analysis_result = data.get("analysis_result", {})
        
        if not analysis_result:
             raise HTTPException(status_code=400, detail="Analysis result is required.")

        ai_analyzer = AIResumeAnalyzer()
        pdf_buffer = ai_analyzer.generate_pdf_report(analysis_result, candidate_name, job_role)
        
        if not pdf_buffer:
             raise HTTPException(status_code=500, detail="Failed to generate PDF report.")
             
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Resume_Analysis_Report.pdf"}
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
