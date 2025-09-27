"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from datetime import datetime
import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from models import Lesson, LessonStatus, generate_lessons
from schemas import CourseCreate, CourseResponse, LessonResponse

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory databases
activities = {
    "Chess Club": {
        "description": "Learn and play chess with your peers",
        "schedule": "Mondays and Wednesdays, 3-4pm",
        "max_participants": 16,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesdays and Thursdays, 4-5:30pm",
        "max_participants": 20,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about scientific discoveries",
        "schedule": "Fridays, 3-4:30pm",
        "max_participants": 15,
        "participants": []
    }
}

courses = {}  # Dictionary to store courses
lessons = {}  # Dictionary to store lessons


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate):
    """Create a new course and generate its lessons"""
    # Generate unique ID for the course
    course_id = str(len(courses) + 1)
    
    # Generate lessons
    course_lessons = generate_lessons(
        course_id=course_id,
        start_date=course.start_date,
        end_date=course.end_date,
        weekday=course.weekday,
        time=course.time
    )
    
    # Store lessons
    lesson_ids = []
    for i, lesson in enumerate(course_lessons):
        lesson_id = f"{course_id}-{i+1}"
        lessons[lesson_id] = lesson
        lesson_ids.append(lesson_id)
    
    # Store course
    course_dict = course.dict()
    course_dict["id"] = course_id
    course_dict["lessons"] = lesson_ids
    courses[course_id] = course_dict
    
    return CourseResponse(**course_dict)


@app.get("/courses", response_model=List[CourseResponse])
def list_courses():
    """List all courses"""
    return [CourseResponse(**course) for course in courses.values()]


@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: str):
    """Get details of a specific course"""
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseResponse(**courses[course_id])


@app.get("/courses/{course_id}/lessons", response_model=List[LessonResponse])
def list_course_lessons(course_id: str):
    """List all lessons for a specific course"""
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = courses[course_id]
    course_lessons = []
    
    for lesson_id in course["lessons"]:
        lesson = lessons[lesson_id]
        lesson_dict = {
            "id": lesson_id,
            "course_id": lesson.course_id,
            "date_time": lesson.date_time,
            "status": lesson.status.value,
            "attendees": lesson.attendees
        }
        course_lessons.append(lesson_dict)
    
    return course_lessons


@app.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: str):
    """Get details of a specific lesson"""
    if lesson_id not in lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson = lessons[lesson_id]
    return {
        "id": lesson_id,
        "course_id": lesson.course_id,
        "date_time": lesson.date_time,
        "status": lesson.status.value,
        "attendees": lesson.attendees
    }


@app.patch("/lessons/{lesson_id}/status")
def update_lesson_status(lesson_id: str, status: LessonStatus):
    """Update the status of a lesson"""
    if lesson_id not in lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson = lessons[lesson_id]
    lesson.status = status
    return {"message": f"Updated lesson status to {status.value}"}
