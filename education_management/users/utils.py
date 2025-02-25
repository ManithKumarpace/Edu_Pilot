import pandas as pd
import random
from datetime import datetime, timedelta
from collections import defaultdict
import os
import traceback
import csv
import json
from education_management import settings


subject_categories = {
    "Mathematics": "main",
    "Science": "main",
    "Social Science": "main",
    "English": "language",
    "Hindi": "language",
    "Sanskrit/French": "language",
    "Environmental Studies": "main",
    "Arts": "other",
    "Health and Physical Education": "other",
    "Music": "other",
    "Sports": "other",
    "Computer Application": "other",
}


# Define subjects for each grade
subjects_per_grade = {
    "1": ["Mathematics", "English", "Hindi", "Arts"],
    "2": ["Mathematics", "English", "Hindi", "Arts"],
    "3": ["Mathematics", "Environmental Studies", "English", "Hindi", "Arts"],
    "4": ["Mathematics", "Environmental Studies", "Science", "English", "Hindi", "Arts"],
    "5": ["Mathematics", "Environmental Studies", "Science", "English", "Hindi", "Arts", "Health and Physical Education", "Sports"],
    "6": ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit/French", "Arts", "Health and Physical Education", "Music", "Sports"],
    "7": ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit/French", "Arts", "Health and Physical Education", "Music", "Sports"],
    "8": ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit/French", "Arts", "Health and Physical Education", "Music", "Sports"],
    "9": ["Mathematics", "Science", "Social Science", "Computer Application", "English", "Hindi", "Arts", "Health and Physical Education", "Music", "Sports"],
    "10": ["Mathematics", "Science", "Social Science", "Computer Application", "English", "Hindi", "Arts", "Health and Physical Education", "Music", "Sports"],
}


def generate_exam_timetable(csv_file, start_date, end_date):
    try:
        df = pd.read_csv(csv_file)  # Load subjects CSV
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        total_days = (end_date - start_date).days + 1
        date_slots = [
            start_date + timedelta(days=i)
            for i in range(total_days)
        ]

        # Identify Sundays
        sundays = [date for date in date_slots if date.weekday() == 6]
        # Sunday = 6

        # Remove Sundays from available slots
        available_dates = [date for date in date_slots if date not in sundays]

        timetable = []
        subject_schedule = defaultdict(list)
        # Track when each subject is scheduled

        for index, row in df.iterrows():
            class_name = int(row.iloc[0])
            # First column is class (convert to int)
            subjects = row.iloc[1:].dropna().tolist()  # Remove NaN values
            num_subjects = len(subjects)

            exam_dates = []
            temp_dates = available_dates[:]  # Copy available dates

            # Calculate gaps dynamically
            remaining_days = len(temp_dates)
            if remaining_days > num_subjects:
                gap_days = (
                    remaining_days - num_subjects
                ) // num_subjects  # Even gaps
            else:
                gap_days = 0  # No extra gaps possible

            for subject in subjects:
                if exam_dates:
                    # Ensure proper gaps based on calculated gap days
                    if class_name <= 3 or gap_days > 0:
                        for _ in range(min(gap_days, len(temp_dates))):
                            temp_dates.pop(0)  # Add a gap by skipping days

                    # Avoid subject clashes for higher classes (7-10)
                    for i, exam_date in enumerate(temp_dates):
                        if subject not in subject_schedule[
                            exam_date.strftime("%d-%b-%Y")
                        ]:
                            break
                    else:
                        i = 0  # Fallback if no non-clashing date found
                    temp_dates = temp_dates[i:]  # Assign only from valid dates

                if temp_dates:
                    exam_date = temp_dates.pop(0)  # Assign next available date
                    session = random.choice(["Morning", "Afternoon"])
                    # Random session
                    exam_dates.append((exam_date, subject, session))
                    subject_schedule[
                        exam_date.strftime("%d-%b-%Y")
                    ].append(subject)  # Mark subject as scheduled

            # Add to timetable
            for exam_date, subject, session in exam_dates:
                timetable.append(
                    [
                        exam_date.strftime("%d-%b-%Y"),
                        class_name,
                        subject,
                        session
                    ]
                )

        # Convert to DataFrame and save
        timetable_df = pd.DataFrame(
            timetable, columns=["Date", "Class", "Subject", "Session"]
        )
        output_dir = os.path.join('static', 'exam_timetables')
        os.makedirs(output_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(
            settings.MEDIA_ROOT,
            'exam_timetables',
            f'exam_timetable_{current_time}.csv'
        )
        generated_csv_path = f"exam_timetables/exam_timetable_{current_time}.csv"
        timetable_df.to_csv(output_path, index=False)
        return generated_csv_path
    except Exception:
        traceback.print_exc()


# Read teacher data from CSV
def read_teachers_from_csv(csv_filepath):
    teachers = []

    with open(csv_filepath, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            teacher_name = row["teacher"].strip()
            role = "normal"
            class_list = row["classes"].split(",")
            # Convert "1,2" to ["1", "2"]
            subject_list = row["subjects"].split(",")
            # Convert "Mathematics,Science" to ["Mathematics", "Science"]

            # Clean up whitespace
            class_list = [cls.strip() for cls in class_list]
            subject_list = [subj.strip() for subj in subject_list]

            # Generate class-subject pairs
            class_subjects = [
                [cls, subj]
                for cls in class_list
                for subj in subject_list
            ]

            # Determine level based on the first class
            level = "higher" if int(class_list[0]) > 4 else "lower"

            # Teacher dictionary
            teacher = {
                "name": teacher_name,
                "role": role,
                "level": level,
                "class_subjects": class_subjects
            }
            teachers.append(teacher)

    return teachers


# Function to generate class sections
def generate_classes():
    return [
        f"{grade}{section}" for grade in range(1, 11) for section in [
            'A',
            'B',
            'C',
            'D'
        ]
    ]


# Group subjects by grade level
def group_subjects_by_grade(classes):
    subjects_by_grade = defaultdict(lambda: defaultdict(list))

    for class_code in classes:
        grade = int(class_code[:-1])
        subjects = subjects_per_grade.get(str(grade), [])
        level = "lower" if grade <= 4 else "higher"

        for subject in subjects:
            subjects_by_grade[level][subject].append(class_code)

    return subjects_by_grade


# Assign class teachers from the imported teacher list
def assign_class_teachers(teachers):
    class_teachers = {}
    assigned_teachers = set()

    for class_code in generate_classes():
        grade = class_code[:-1]  # Extract grade number (e.g., "1A" -> "1")

        # Find teachers handling this grade (not section-based)
        eligible_teachers = [
            teacher
            for teacher in teachers
            if any(cls == grade for cls, subj in teacher["class_subjects"])
        ]

        if eligible_teachers:
            # Randomly select a class teacher (if not already assigned)
            available_teachers = [
                t
                for t in eligible_teachers
                if t["name"] not in assigned_teachers
            ]
            if available_teachers:
                class_teacher = random.choice(available_teachers)
                class_teacher["role"] = f"class teacher of {class_code}"
                assigned_teachers.add(class_teacher["name"])
                class_teachers[class_code] = class_teacher["name"]
    return teachers


# Function to balance the teaching load
def redistribute_teaching_load(teachers):
    teacher_section_count = {
        teacher["name"]: len(teacher["class_subjects"])
        for teacher in teachers
    }

    underloaded_teachers = {
        t["name"]: t
        for t in teachers
        if teacher_section_count[t["name"]] <= 3
    }
    overloaded_teachers = {
        t["name"]: t
        for t in teachers
        if teacher_section_count[t["name"]] > 5
    }

    for overloaded_name, overloaded_teacher in overloaded_teachers.items():
        extra_assignments = overloaded_teacher["class_subjects"][5:]
        overloaded_teacher["class_subjects"] = overloaded_teacher[
            "class_subjects"
        ][:5]

        for underloaded_name, underloaded_teacher in underloaded_teachers.items():
            if len(underloaded_teacher["class_subjects"]) < 3:
                underloaded_teacher[
                    "class_subjects"
                ].extend(extra_assignments[:3])
                extra_assignments = extra_assignments[3:]

            if not extra_assignments:
                break

    return teachers


# Merge teachers handling only "other" subjects
def merge_other_subject_teachers(teachers):
    merged_teachers = {}

    for teacher in teachers:
        teacher_name = teacher["name"]
        class_subjects = teacher["class_subjects"]

        if all(
            subject_categories[subj] == "other" for _, subj in class_subjects
        ):
            if teacher_name not in merged_teachers:
                merged_teachers[teacher_name] = {
                    "name": teacher_name,
                    "role": teacher["role"],
                    "level": teacher["level"],
                    "class_subjects": []
                }
            merged_teachers[
                teacher_name
            ]["class_subjects"].extend(class_subjects)
        else:
            merged_teachers[teacher_name] = teacher

    return list(merged_teachers.values())


# Assign extra subject to teachers with minimum load
def assign_extra_subject_to_min_teachers(
        teachers,
        subject_name="General Knowledge"
    ):
    main_teachers = [t for t in teachers if t["level"] == "higher"]

    main_teachers.sort(key=lambda t: len(t["class_subjects"]))

    selected_teachers = main_teachers[:4]

    extra_subject_assignments = [
        [["9A", subject_name], ["9B", subject_name]],
        [["9C", subject_name], ["9D", subject_name]],
        [["10A", subject_name], ["10B", subject_name]],
        [["10C", subject_name], ["10D", subject_name]]
    ]

    for teacher, extra_classes in zip(selected_teachers, extra_subject_assignments):
        teacher["class_subjects"].extend(extra_classes)

    return teachers


def expand_class_subjects(teachers, sections=4):
    expanded_teachers = []

    for teacher in teachers:
        expanded_class_subjects = []

        for cls, subject in teacher["class_subjects"]:
            for section in range(sections):
                section_label = chr(65 + section)  # 'A', 'B', 'C', 'D', etc.
                expanded_class_subjects.append(
                    [
                        f"{cls}{section_label}",
                        subject
                    ]
                )

        expanded_teachers.append({
            "name": teacher["name"],
            "role": teacher["role"],
            "level": teacher["level"],
            "class_subjects": expanded_class_subjects
        })

    return expanded_teachers


def teacher_csv_to_json(csv_filepath):
    teachers = read_teachers_from_csv(csv_filepath)
    updated_teachers = assign_class_teachers(teachers)
    balanced_teachers = redistribute_teaching_load(updated_teachers)
    final_teachers = merge_other_subject_teachers(balanced_teachers)
    final_teachers = assign_extra_subject_to_min_teachers(final_teachers)
    expanded_teachers = expand_class_subjects(final_teachers)
    json_dump = json.dump(expanded_teachers, indent=2)
    return json_dump


def timetable_generation(subject_csv, teacher_csv):
    teachers = teacher_csv_to_json(teacher_csv)
    subjects_by_grade = defaultdict(list)
    reader = csv.reader(subject_csv)
    next(reader)  # Skip header
    for row in reader:
        grade = int(row[0])
        subjects = [s.strip() for s in row[2:] if s.strip()]
        subjects_by_grade[grade] = subjects

    # Generate all classes (1A to 10D or 1A to 10F based on section count)
    all_classes = []

    def generate_classes(grade_range=(1, 10), section_count=4):
        sections = [chr(65 + i) for i in range(section_count)]  # 'A' -> 'D' or 'A' -> 'F'
        return [f"{grade}{section}" for grade in range(grade_range[0], grade_range[1] + 1) for section in sections]

    # Example usage
    section_count = 4  # Change to 4 or 6 dynamically
    all_classes = generate_classes(section_count=section_count)

    # Step 2: Generate class timetables
    class_timetables = defaultdict(dict)

    # Days of the week
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    for cls in all_classes:
        grade = int(cls[:-1])
        num_periods = 5 if grade <= 4 else 8
        subjects = subjects_by_grade.get(grade, [])

        # Get class teacher's subject
        class_teacher = next((t for t in teachers if f"class teacher of {cls}" in t["role"]), None)
        if class_teacher:
            main_subject = class_teacher["class_subjects"][0][1]
        else:
            main_subject = ["class_subjects"][0][1]

        # Initialize timetable with class teacher's subject in first
        timetable = {day: [main_subject] + [''] * (num_periods - 1) for day in days}

        # Collect other subjects
        other_subjects = [subj for subj in subjects if subj != main_subject]

        # Track subject counts
        subject_counts = {subj: 0 for subj in subjects}
        subject_counts[main_subject] = 6  # Taught once each day

        # Define subject types
        main_subjects = {'Mathematics', 'Science', 'Social Science','Environment Studies'}
        languages = {'English', 'Hindi', 'Sanskrit/French'}
        other = {'Arts', 'Health and Physical Education', 'Music', 'Sports', 'Computer Application', 'General Knowledge'}

        # Distribute subjects
        for day in days:
            # Assign main subjects (up to 2 per day)
            main_assigned = 0
            for subj in other_subjects:
                if subj in main_subjects and subject_counts.get(subj, 0) < 12:  # 2 per day * 6 days
                    for period in [1, 2]:  # Assign to first available periods after first
                        if timetable[day][period] == '':
                            timetable[day][period] = subj
                            subject_counts[subj] += 1
                            main_assigned += 1
                            break
                    if main_assigned >= 2:
                        break

            # Assign languages up to 5 per week
            for subj in other_subjects:
                if subj in languages and subject_counts.get(subj, 0) < 5:
                    for period in range(1, num_periods):
                        if timetable[day][period] == '':
                            timetable[day][period] = subj
                            subject_counts[subj] += 1
                            break

            # Assign secondary subjects twice a week
            for subj in other_subjects:
                if subj in other and subject_counts.get(subj, 0) < 2:
                    for period in range(num_periods - 1, 0, -1):  # Prefer later periods
                        if timetable[day][period] == '':
                            timetable[day][period] = subj
                            subject_counts[subj] += 1
                            break

        # Ensure sports in periods 6-8 for higher classes
        if grade >= 5 and 'Sports' in subjects:
            for day in days:
                if 'Sports' in timetable[day]:
                    sport_period = timetable[day].index('Sports')
                    if sport_period < 5:  # Move to 6-8
                        timetable[day][sport_period] = ''
                        for period in [5, 6, 7]:
                            if timetable[day][period] == '':
                                timetable[day][period] = 'Sports'
                                break

        class_timetables[cls] = timetable

    class_timetable = json.dump(class_timetables, indent=2)

    # Step 3: Generate teacher timetables
    teacher_schedules = defaultdict(lambda: defaultdict(lambda: [''] * 8))

    for cls in all_classes:
        grade = int(cls[:-1])
        num_periods = 5 if grade <= 4 else 8
        timetable = class_timetables[cls]
        for day in days:
            for period in range(num_periods):
                subject = timetable[day][period]
                if not subject:
                    continue
                # Find the teacher for this subject and class
                teacher = next((t for t in teachers if [cls, subject] in t['class_subjects']), None)
                if teacher:
                    teacher_name = teacher['name']
                    if period < len(teacher_schedules[teacher_name][day]):
                        if teacher_schedules[teacher_name][day][period] == '':
                            teacher_schedules[teacher_name][day][period] = cls
                        else:
                            # Handle conflict by finding next available period
                            for p in range(period, 8):
                                if teacher_schedules[teacher_name][day][p] == '':
                                    teacher_schedules[teacher_name][day][p] = cls
                                    break
    # Step 4: Adjust Saturday timetable
    senior_classes = [cls for cls in all_classes if int(cls[:-1]) >= 7]  # Grades 7-10
    random.shuffle(senior_classes)  # Randomly select 3 classes
    sports_classes = senior_classes[:3]

    for cls in all_classes:
        grade = int(cls[:-1])
        num_periods = 5 if grade <= 4 else 8
        saturday_schedule = class_timetables[cls]['saturday']

        # Count empty periods
        empty_periods = [i for i, subj in enumerate(saturday_schedule) if not subj]

        # If more than one period is missing, fill with main subjects
        if len(empty_periods) > 1:
            main_subjects = [subj for subj in subjects_by_grade[grade] if subj in {'Mathematics', 'Science', 'Social Science', 'Environment Studies'}]
            random.shuffle(main_subjects)  # Shuffle to distribute evenly

            for i in empty_periods:
                if main_subjects:
                    saturday_schedule[i] = main_subjects.pop(0)
                else:
                    break  # If all main subjects are used, stop filling

        # Assign Sports to three random senior classes in periods 7 & 8
        if cls in sports_classes and num_periods == 8:
            saturday_schedule[6] = 'Sports'
            saturday_schedule[7] = 'Sports'

    # Convert teacher schedules to the required format
    formatted_teacher_timetables = {}
    for teacher, schedule in teacher_schedules.items():
        formatted = {}
        for day in days:
            periods = schedule[day][:8]  # Ensure max 8 periods
            formatted[day] = periods
        formatted_teacher_timetables[teacher] = formatted

    teachers_timetable = json.dump(formatted_teacher_timetables, indent=2)

    return class_timetable , teachers_timetable
