# tests/test_attendance.py
import pytest
from sis_app.models import Attendance, Enrollment

@pytest.mark.django_db
class TestAttendanceManagement:
    def test_save_and_update_attendance(self, enrollment):
        """Checks that attendance records are correctly saved and updated for each student."""
        att = Attendance.objects.create(
            enrollment=enrollment,
            total_classes=10,
            attended_classes=8
        )
        assert att.total_classes == 10
        assert att.attended_classes == 8
        assert att.percentage == 80.00

        # Update
        att.attended_classes = 9
        att.save()
        att.refresh_from_db()
        assert att.attended_classes == 9
        assert att.percentage == 90.00

    def test_attendance_percentage_calculation(self, enrollment):
        """Ensures the accuracy of attendance percentage calculations."""
        att = Attendance.objects.create(
            enrollment=enrollment,
            total_classes=10,
            attended_classes=8
        )
        assert att.percentage == 80.00

        att.total_classes = 0
        att.save()
        att.refresh_from_db()
        assert att.percentage == 0

        att.total_classes = 5
        att.attended_classes = 5
        att.save()
        att.refresh_from_db()
        assert att.percentage == 100.00