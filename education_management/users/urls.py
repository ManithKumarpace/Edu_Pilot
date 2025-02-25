from django.urls import path
from users.views import (
    Index,
    TimeTableAgent,
    ExamTimeTableView,
    ClassTimeTable,
    EduHelper
)

app_name = "edupilot"

urlpatterns = [
    path('', Index, name="index"),
    path('timetable/', TimeTableAgent, name="timetable"),
    path('exam-timetable/', ExamTimeTableView, name="examtimetable"),
    path('class-timetable/', ClassTimeTable, name="classtimetable"),
    path('eduhelper/', EduHelper, name="eduhelper")
]
