import csv
import os
from django.shortcuts import render
from datetime import datetime
from education_management import settings
from users.models import ExamTimeTable, SchoolTimeTable
from users.utils import generate_exam_timetable, timetable_generation


# Create your views here.
def Index(request):
    return render(request, 'index.html')


def TimeTableAgent(request):
    return render(request, 'TimeTableAgent.html')


def ClassTimeTable(request):
    error_message = ""
    if request.method == "POST":
        try:
            print("post method triggred")
            teachers_csv = request.FILES["teachers_csv"]
            subject_csv = request.FILES["subject_csv"]
            if not subject_csv or not teachers_csv:
                error_message = "Upload both the csv files"
            else:
                schooltimetable_obj = SchoolTimeTable.objects.create(
                    subjects_csv=subject_csv,
                    teachers_data_csv=teachers_csv
                )
                class_timetable, teachers_timetable = timetable_generation(
                    schooltimetable_obj.subjects_csv,
                    schooltimetable_obj.teachers_data_csv
                )
                print("\n\n\n\n\n class_timetable", class_timetable, teachers_timetable)
        except Exception as e:
            error_message = str(e)
    context = {
        "error_message": error_message
    }
    return render(request, 'ClassTimeTable.html', context)


def ExamTimeTableView(request):
    error_message = ""
    generated_csv_path = ""
    timetable_data = ""
    if request.method == "POST":
        try:
            start_date_str = request.POST.get("start-date")
            end_date_str = request.POST.get("end-date")
            start_date = datetime.strptime(
                start_date_str,
                "%Y-%m-%d"
            )
            end_date = datetime.strptime(
                end_date_str,
                "%Y-%m-%d"
            )
            csv_file = request.FILES['csv-upload']

            if not csv_file.name.endswith('.csv'):
                error_message = 'File is not CSV type'
            else:
                exam_timetable_obj = ExamTimeTable.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    uploaded_csv=csv_file
                )
                generated_csv_path = generate_exam_timetable(
                    exam_timetable_obj.uploaded_csv,
                    start_date_str,
                    end_date_str
                )
                exam_timetable_obj.generated_timetable_csv = generated_csv_path
                exam_timetable_obj.save()

                with open(os.path.join(settings.MEDIA_ROOT, generated_csv_path), 'r') as f:
                    reader = csv.DictReader(f)
                    timetable_data = list(reader)
                print(timetable_data)
        except Exception as e:
            error_message = str(e)
    print("generated_csv_path", generated_csv_path)
    context = {
        "error_message": error_message,
        "generated_csv_path": generated_csv_path,
        "timetable_data": timetable_data
    }
    return render(request, 'ExamTimeTable.html', context)


def EduHelper(request):
    try:
        context = {}
        return render(request, "eduhelper.html", context)
    except Exception as e:
        print(str(e))