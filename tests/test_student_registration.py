# tests/test_student_registration.py
import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from sis_app.models import Student
from decimal import Decimal

@pytest.mark.django_db
class TestStudentRegistration:
    def test_create_student_with_all_details_succeeds(self, student):
        """Ensures all student details are correctly captured and validated."""
        assert student.reg_no == 'TEST001'
        assert student.first_name == 'Test'
        assert student.last_name == 'Student'
        assert student.date_of_birth == date(2000, 1, 1)
        assert student.roll_no == 'ROLL001'
        assert student.batch == '2020'
        assert student.degree == 'BTech'
        assert student.course == 'CSE'
        assert student.semester == 1
        assert student.sgpa == Decimal('8.50')
        assert student.cgpa == Decimal('8.20')
        assert student.age == 25  # As of Oct 30, 2025
        student.full_clean()  # Validates all fields

    def test_duplicate_reg_no_prevented(self, student):
        """Confirms that duplicate entries are prevented."""
        with pytest.raises(IntegrityError):
            Student.objects.create(
                reg_no='TEST001',  # Duplicate PK/unique
                first_name='Duplicate',
                last_name='Test',
                date_of_birth=date(2000, 1, 1),
                roll_no='ROLL002',
                batch='2020',
                degree='BTech',
                course='CSE',
                semester=1
            )

    @pytest.mark.parametrize("missing_field,value", [
        ("first_name", ""),
        ("last_name", ""),
        ("date_of_birth", None),
        ("roll_no", ""),
        ("batch", ""),
        ("degree", ""),
        ("course", ""),
        ("semester", None)
    ])
    def test_mandatory_fields_required(self, student, missing_field, value):
        """Verifies that mandatory fields cannot be left blank."""
        setattr(student, missing_field, value)
        with pytest.raises(ValidationError):
            student.full_clean()

    def test_password_methods(self, student):
        """Tests password setting and checking for students."""
        raw_pass = 'testpass123'
        student.set_password(raw_pass)
        assert student.check_password(raw_pass) is True
        assert student.must_change_password is False

        # Admin default
        new_student = Student.objects.create(
            reg_no='ADMIN001',
            first_name='AdminTest',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            roll_no='ROLL003',
            batch='2020',
            degree='BTech',
            course='CSE',
            semester=1
        )
        new_student.set_password_admin_default('defaultpass')
        assert new_student.check_password('defaultpass') is True
        assert new_student.must_change_password is True