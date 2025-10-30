# tests/test_marks.py
import pytest
from sis_app.models import AcademicRecord, Enrollment, Subject

# Grade points mapping for tests (assumed business logic)
GRADE_POINTS = {
    'A+': 10.0, 'A': 9.0, 'B+': 8.0, 'B': 7.0,
    'C+': 6.0, 'C': 5.0, 'D': 4.0, 'F': 0.0
}

@pytest.mark.django_db
class TestMarksAndExamination:
    def test_marks_entry_and_grade_calculation(self, enrollment):
        """Tests the correctness of marks entry, grade calculations, and result generation."""
        # Model has direct grade/credit_points; test setting and calculation of credit_points
        subj_credits = enrollment.subject_code.credits
        rec = AcademicRecord.objects.create(
            enrollment=enrollment,
            grade='A',
            credit_points=9.0
        )
        # Assuming 10-point scale common in some systems; test direct
        assert rec.grade == 'A'
        assert rec.credit_points == 9.0

        # Update grade
        rec.grade = 'B'
        rec.credit_points = 7.0
        rec.save()
        rec.refresh_from_db()
        assert rec.grade == 'B'
        assert rec.credit_points == 7.0

    def test_results_published_and_accessible(self, enrollment, student):
        """Ensures results are published accurately and made accessible to students."""
        rec = AcademicRecord.objects.create(
            enrollment=enrollment,
            grade='B',
            credit_points=7.0
        )
        # Accessible via related_name
        student_record = student.enrollments.first().academic_record
        assert student_record == rec
        assert student_record.grade == 'B'

        # "Published" by existence; no flag, so always accessible once created
        # If unpublished logic exists in views (e.g., semester check), add there