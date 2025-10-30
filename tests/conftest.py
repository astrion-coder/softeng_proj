# tests/conftest.py
import pytest
from datetime import date
from sis_app.models import Student, Subject, Enrollment, Attendance, AcademicRecord
from decimal import Decimal

pytestmark = pytest.mark.django_db

@pytest.fixture
def student():
    return Student.objects.create(
        reg_no='TEST001',
        first_name='Test',
        last_name='Student',
        date_of_birth=date(2000, 1, 1),
        roll_no='ROLL001',
        batch='2020',
        degree='BTech',
        course='CSE',
        semester=1,
        sgpa=Decimal('8.50'),
        cgpa=Decimal('8.20')
    )

@pytest.fixture
def subject():
    return Subject.objects.create(
        subject_code='CS101',
        subject_name='Intro to CS',
        credits=4,
        semester=1
    )

@pytest.fixture
def enrollment(student, subject):
    return Enrollment.objects.create(
        reg_no=student,
        subject_code=subject,
        semester=1
    )

@pytest.fixture
def attendance(enrollment):
    return Attendance.objects.create(
        enrollment=enrollment,
        total_classes=10,
        attended_classes=8
    )

@pytest.fixture
def academic_record(enrollment):
    return AcademicRecord.objects.create(
        enrollment=enrollment,
        grade='A',
        credit_points=9.0
    )