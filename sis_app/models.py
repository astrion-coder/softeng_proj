from django.db import models
from datetime import date
from django.contrib.auth.hashers import make_password, check_password

class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    
    class Meta:
        verbose_name_plural = "People"
    
    @property
    def age(self):
        """Derived attribute: Calculate age from date of birth"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


from django.contrib.auth.hashers import make_password, check_password

class Student(Person):
    """Generalization: Student IS A Person"""
    reg_no = models.CharField(max_length=20, unique=True, primary_key=True)
    roll_no = models.CharField(max_length=20)
    batch = models.CharField(max_length=10)
    degree = models.CharField(max_length=50)
    course = models.CharField(max_length=100)
    semester = models.IntegerField()
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    password_hash = models.CharField(max_length=128, blank=True)
    must_change_password = models.BooleanField(default=False)

    def set_password(self, raw_password):
        """
        Student changes their own password.
        Hashes the password and marks must_change_password=False.
        Saves immediately.
        """
        self.password_hash = make_password(raw_password)
        self.must_change_password = False
        self.save(update_fields=['password_hash', 'must_change_password'])

    def set_password_admin_default(self, raw_password):
        """
        Admin sets default password for a new student.
        Hashes the password and marks must_change_password=True.
        """
        self.password_hash = make_password(raw_password)
        self.must_change_password = True


    def check_password(self, raw_password):
        """Verify a raw password against the stored hash."""
        if not self.password_hash:
            return False
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return f"{self.reg_no} - {self.first_name} {self.last_name}"



class Subject(models.Model):
    subject_code = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=200)
    credits = models.IntegerField()
    semester = models.IntegerField()
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    reg_no = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject_code = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.IntegerField()
    
    class Meta:
        unique_together = ('reg_no', 'subject_code', 'semester')
    
    def __str__(self):
        return f"{self.reg_no} enrolled in {self.subject_code}"


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='attendance')
    total_classes = models.IntegerField(default=0)
    attended_classes = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Attendance Records"
    
    @property
    def percentage(self):
        """Derived attribute: Calculate attendance percentage"""
        if self.total_classes == 0:
            return 0
        return round((self.attended_classes / self.total_classes) * 100, 2)
    
    def __str__(self):
        return f"Attendance for {self.enrollment}"


class AcademicRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='academic_record')
    grade = models.CharField(max_length=2, choices=[
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F')
    ])
    credit_points = models.DecimalField(max_digits=4, decimal_places=2)
    
    def __str__(self):
        return f"Grade: {self.grade} for {self.enrollment}"