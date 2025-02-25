from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=100)

    # Required fields for Django's admin interface
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Administrator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='administrator'
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'administrators'

    def __str__(self):
        return self.name


class Division(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
    C = 'C', 'C'
    D = 'D', 'D'
    E = 'E', 'E'
    F = 'F', 'F'


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=255)
    division = models.CharField(
        max_length=1,
        choices=Division.choices,
        default=Division.A
    )
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classes'
        verbose_name_plural = 'classes'

    def __str__(self):
        return f"{self.class_name} - Division {self.division}"


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return self.subject_name


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='teacher'
    )
    name = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    designation = models.CharField(max_length=100)
    classes = models.ManyToManyField(Class, related_name='teachers')
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teachers'

    def __str__(self):
        return self.name


class Rank(models.TextChoices):
    FIRST = 'FIRST', 'First'
    SECOND = 'SECOND', 'Second'
    THIRD = 'THIRD', 'Third'


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='student'
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    roll_number = models.IntegerField()
    class_enrolled = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='students'
    )
    rank = models.CharField(
        max_length=6,
        choices=Rank.choices,
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(default=False)
    class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        unique_together = ['roll_number', 'class_enrolled']
        # Ensures unique roll numbers within a class

    def __str__(self):
        return f"{
            self.first_name
        } {
            self.last_name
        } - Roll No: {
            self.roll_number
        }"


class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='parent'
    )
    name = models.CharField(max_length=255)
    students = models.ManyToManyField(Student, related_name='parents')
    is_guardian = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'parents'

    def __str__(self):
        return self.name


class QuestionType(models.TextChoices):
    DESCRIPTIVE = 'DESCRIPTIVE', 'Descriptive'
    MCQ = 'MCQ', 'Multiple Choice Questions'


class QuestionPaper(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='question_papers'
    )
    class_level = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='question_papers'
    )
    is_sample = models.BooleanField(default=False)
    created_by = models.UUIDField(null=True, blank=True)
    question_type = models.CharField(
        max_length=11,
        choices=QuestionType.choices,
        default=QuestionType.DESCRIPTIVE
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'question_papers'

    def __str__(self):
        return f"{self.subject} - {self.class_level} ({self.question_type})"


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_name = models.CharField(max_length=255)
    class_level = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    question_paper = models.ForeignKey(
        QuestionPaper,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    created_by = models.UUIDField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'exams'

    def __str__(self):
        return f"{self.exam_name} - {self.subject} ({self.class_level})"


class Grade(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
    C = 'C', 'C'
    D = 'D', 'D'
    E = 'E', 'E'
    F = 'F', 'F'


class StudentAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    marks_obtained = models.FloatField()
    grade = models.CharField(
        max_length=1,
        choices=Grade.choices,
        default=Grade.F
    )
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_assessments'
        unique_together = ['exam', 'student']
        # Prevents duplicate entries for same student and exam

    def __str__(self):
        return f"{self.student} - {self.exam} (Grade: {self.grade})"


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date_of_attendance = models.DateField()
    is_present = models.BooleanField(default=False)
    class_attended = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_attendances'
        unique_together = ['student', 'date_of_attendance', 'class_attended']
        # Prevents duplicate attendance entries

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{
            self.student
        } - {
            self.class_attended
        } - {
            self.date_of_attendance
        } ({status})"


class StudentReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    report_link = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_reports'

    def __str__(self):
        return f"Report for {self.student}"


class ExamTimeTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    uploaded_csv = models.FileField(upload_to="")
    generated_timetable_csv = models.FileField(
        upload_to="",
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'exam_timetable'

    def __str__(self):
        return f"Exam Timetable: {self.id}"


class SchoolTimeTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subjects_csv = models.FileField(upload_to="")
    teachers_data_csv = models.FileField(upload_to="")
    generated_timetable_csv = models.FileField(
        upload_to="",
        null=True,
        blank=True
    )

    class Meta:
        db_table = "school_timetable"

    def __str__(self):
        return f"School Timetable: {self.id}"
