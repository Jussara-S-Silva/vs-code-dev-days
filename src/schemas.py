from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CourseCreate(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    weekday: int  # 0-6 (Monday-Sunday)
    time: str  # Format: "HH:MM"
    price_per_lesson: float
    max_participants: int

class CourseResponse(CourseCreate):
    id: str
    lessons: List[str]  # List of lesson IDs

class LessonResponse(BaseModel):
    id: str
    course_id: str
    date_time: datetime
    status: str
    attendees: List[str]