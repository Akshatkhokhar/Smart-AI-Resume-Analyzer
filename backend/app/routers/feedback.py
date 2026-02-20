from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.feedback.feedback import FeedbackManager

router = APIRouter()

class FeedbackModel(BaseModel):
    rating: int
    usability_score: int
    feature_satisfaction: int
    missing_features: str
    improvement_suggestions: str
    user_experience: str

@router.post("/")
def submit_feedback(feedback: FeedbackModel):
    manager = FeedbackManager()
    # Get dict representation
    data = feedback.dict()
    success = manager.save_feedback(data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save feedback")
    return {"message": "Feedback submitted successfully"}

@router.get("/")
def get_feedback():
    manager = FeedbackManager()
    return manager.get_all_feedback()
