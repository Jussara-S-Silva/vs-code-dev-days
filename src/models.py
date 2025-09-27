from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

class LessonStatus(Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Lesson:
    def __init__(
        self,
        course_id: str,
        date_time: datetime,
        status: LessonStatus = LessonStatus.SCHEDULED,
        attendees: Optional[List[str]] = None
    ):
        self.course_id = course_id
        self.date_time = date_time
        self.status = status
        self.attendees = attendees or []

def generate_lessons(
    course_id: str,
    start_date: datetime,
    end_date: datetime,
    weekday: int,  # 0 = Monday, 6 = Sunday
    time: str,  # Format: "HH:MM"
) -> List[Lesson]:
    """Generate lessons for a course based on schedule."""
    lessons = []
    current_date = start_date

    # Convert time string to hours and minutes
    hour, minute = map(int, time.split(":"))

    while current_date <= end_date:
        # If current day matches weekday
        if current_date.weekday() == weekday:
            # Create lesson at specified time
            lesson_datetime = current_date.replace(hour=hour, minute=minute)
            lessons.append(Lesson(course_id=course_id, date_time=lesson_datetime))
        
        current_date += timedelta(days=1)

    return lessons