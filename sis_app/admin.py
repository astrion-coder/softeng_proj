from django.contrib import admin
from .models import Person, Student, Subject, Enrollment, Attendance, AcademicRecord


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_id', 'first_name', 'last_name', 'date_of_birth', 'get_age')
    search_fields = ('first_name', 'last_name')
    list_filter = ('date_of_birth',)
    
    def get_age(self, obj):
        return obj.age
    get_age.short_description = 'Age'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('reg_no', 'first_name', 'last_name', 'roll_no', 'batch', 'degree', 'semester', 'sgpa', 'cgpa', 'must_change_password')
    search_fields = ('reg_no', 'roll_no', 'first_name', 'last_name')
    list_filter = ('batch', 'degree', 'semester')
    readonly_fields = ('password_hash',)  # admin can't see/change the password directly
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth')
        }),
        ('Academic Information', {
            'fields': ('reg_no', 'roll_no', 'batch', 'degree', 'course', 'semester', 'sgpa', 'cgpa')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new students
            obj.set_password_admin_default("default123")  # just sets fields
            super().save_model(request, obj, form, change)  # actually saves to DB


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'credits', 'semester')
    search_fields = ('subject_code', 'subject_name')
    list_filter = ('semester', 'credits')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'reg_no', 'subject_code', 'semester')
    search_fields = ('reg_no__reg_no', 'subject_code__subject_code')
    list_filter = ('semester',)
    autocomplete_fields = ['reg_no', 'subject_code']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('attendance_id', 'enrollment', 'total_classes', 'attended_classes', 'get_percentage')
    search_fields = ('enrollment__reg_no__reg_no',)
    
    def get_percentage(self, obj):
        return f"{obj.percentage}%"
    get_percentage.short_description = 'Attendance %'


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'enrollment', 'grade', 'credit_points')
    search_fields = ('enrollment__reg_no__reg_no', 'enrollment__subject_code__subject_code')
    list_filter = ('grade',)