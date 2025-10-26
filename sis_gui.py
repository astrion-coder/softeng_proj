#!/usr/bin/env python3
"""
sis_gui.py

Tkinter GUI frontend for the student_info_system Django project.

Place this file next to manage.py and run:
    python sis_gui.py

Requirements:
 - Python (same env as your Django project)
 - Django project must be configured and migrated
"""

import os
import sys
import django
import traceback
from datetime import datetime

# --- Django environment bootstrapping ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_info_system.settings')
django.setup()

from sis_app.models import Student, Subject, Enrollment, Attendance, AcademicRecord

import tkinter as tk
from tkinter import ttk, messagebox

# --- Helper utilities ---
def safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

def parse_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None

# --- Main Application Class ---
class SISApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Information System - Desktop Client")
        self.geometry("980x640")
        self.resizable(True, True)

        # Styling
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

        # Current logged-in student
        self.student = None

        # Build login UI first
        self._build_login_ui()

    # -------------------------
    # Login UI
    # -------------------------
    def _build_login_ui(self):
        for child in self.winfo_children():
            child.destroy()

        frame = ttk.Frame(self, padding=28)
        frame.pack(expand=True)

        ttk.Label(frame, text="Student Login", font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        # Registration number
        ttk.Label(frame, text="Registration Number:").grid(row=1, column=0, sticky='e', padx=(0,8), pady=6)
        self.login_regno_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.login_regno_var, width=30).grid(row=1, column=1, sticky='w', pady=6)
        ttk.Label(frame, text="(Example : 1001)").grid(row=2, column=1, sticky='w', pady=(0,10))

        # Password entry
        ttk.Label(frame, text="Password:").grid(row=3, column=0, sticky='e', padx=(0,8), pady=6)
        self.login_password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.login_password_var, show="•", width=30).grid(row=3, column=1, sticky='w', pady=6)

        # Login button
        login_btn = ttk.Button(frame, text="Login", command=self._attempt_login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=12)

        # Info area
        info = ttk.Label(frame, text="Note: Students can edit profile details except SGPA and CGPA.", foreground="#333")
        info.grid(row=5, column=0, columnspan=2, pady=(8,0))

    def _attempt_login(self):
        reg_no = self.login_regno_var.get().strip()
        password = self.login_password_var.get().strip()

        if not reg_no or not password:
            messagebox.showwarning("Input required", "Please enter both registration number and password.")
            return

        try:
            student = Student.objects.filter(reg_no=reg_no).first()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Database error:\n{e}")
            return

        if not student:
            messagebox.showerror("Not found", f"No student found with reg_no: {reg_no}")
            return

        if not student.check_password(password):
            messagebox.showerror("Login failed", "Incorrect password. Please try again.")
            return

        self.student = student

        if getattr(student, 'must_change_password', False):
            messagebox.showinfo("Change password required", "You must change your default password before continuing.")
            ok = self._prompt_change_password(force=True)
            if not ok:
                messagebox.showwarning("Login halted", "You must set a new password to proceed. Login cancelled.")
                self.student = None
                return

        self._build_dashboard()

    # --- Password change ---
    def _prompt_change_password(self, force=False):
        pwd_win = tk.Toplevel(self)
        pwd_win.title("Change Password")
        pwd_win.grab_set()
        pwd_win.geometry("420x220")

        ttk.Label(pwd_win, text="Current Password:" if not force else "Enter current password:").pack(pady=(12,4))
        current_var = tk.StringVar()
        ttk.Entry(pwd_win, textvariable=current_var, show="•", width=40).pack()

        ttk.Label(pwd_win, text="New Password:").pack(pady=(12,4))
        new_var = tk.StringVar()
        ttk.Entry(pwd_win, textvariable=new_var, show="•", width=40).pack()

        ttk.Label(pwd_win, text="Confirm New Password:").pack(pady=(12,4))
        confirm_var = tk.StringVar()
        ttk.Entry(pwd_win, textvariable=confirm_var, show="•", width=40).pack()

        result = {'ok': False}

        def do_change():
            current = current_var.get().strip()
            new = new_var.get().strip()
            confirm = confirm_var.get().strip()

            if not current:
                messagebox.showerror("Required", "Please enter your current password.")
                return
            if not self.student.check_password(current):
                messagebox.showerror("Current password incorrect", "The current password you entered is incorrect.")
                return
            if not new or not confirm:
                messagebox.showerror("Required", "Enter new password and confirmation.")
                return
            if new != confirm:
                messagebox.showerror("Mismatch", "New password and confirmation do not match.")
                return
            if len(new) < 6:
                messagebox.showwarning("Weak password", "Consider using a password with at least 6 characters.")

            try:
                self.student.set_password(new)
                messagebox.showinfo("Success", "Password changed successfully.")
                result['ok'] = True
                pwd_win.destroy()
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to change password:\n{e}")

        def do_cancel():
            pwd_win.destroy()

        btn_frame = ttk.Frame(pwd_win)
        btn_frame.pack(pady=(10,4))
        ttk.Button(btn_frame, text="Change Password", command=do_change).pack(side='left', padx=(0,8))
        ttk.Button(btn_frame, text="Cancel", command=do_cancel).pack(side='left')

        self.wait_window(pwd_win)
        return result['ok']

    # -------------------------
    # Dashboard
    # -------------------------
    def _build_dashboard(self):
        for child in self.winfo_children():
            child.destroy()

        topbar = ttk.Frame(self, padding=(10,8))
        topbar.pack(fill='x')

        ttk.Label(topbar, text=f"Logged in as: {self.student.reg_no} — {self.student.first_name} {self.student.last_name}", font=('Segoe UI', 10, 'bold')).pack(side='left')
        ttk.Button(topbar, text="Logout", command=self._logout).pack(side='right', padx=6)
        ttk.Button(topbar, text="Refresh", command=self._refresh_all_tabs).pack(side='right')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabs
        self.profile_tab = ttk.Frame(self.notebook, padding=12)
        self.subjects_tab = ttk.Frame(self.notebook, padding=12)
        self.enrollments_tab = ttk.Frame(self.notebook, padding=12)
        self.attendance_tab = ttk.Frame(self.notebook, padding=12)
        self.grades_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.profile_tab, text="Profile")
        self.notebook.add(self.subjects_tab, text="Subjects")
        self.notebook.add(self.enrollments_tab, text="Enrollments")
        self.notebook.add(self.attendance_tab, text="Attendance")
        self.notebook.add(self.grades_tab, text="Grades")

        # Build tab UI
        self._build_profile_tab()
        self._build_subjects_tab()
        self._build_enrollments_tab()
        self._build_attendance_tab()
        self._build_grades_tab()

    def _logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.student = None
            self._build_login_ui()

    def _refresh_all_tabs(self):
        if self.student:
            self.student = Student.objects.get(reg_no=self.student.reg_no)
        self._build_profile_tab()
        self._build_subjects_tab()
        self._build_enrollments_tab()
        self._build_attendance_tab()
        self._build_grades_tab()
        messagebox.showinfo("Refreshed", "Data refreshed from the database.")

    # -------------------------
    # Profile Tab
    # -------------------------
    def _build_profile_tab(self):
        for child in self.profile_tab.winfo_children():
            child.destroy()

        s = self.student

        # Main frames
        left = ttk.Frame(self.profile_tab, padding=(10,10), style="Card.TFrame")
        left.pack(side='left', fill='y', padx=(0,20), pady=10)

        right = ttk.Frame(self.profile_tab, padding=(10,10), style="Card.TFrame")
        right.pack(side='left', fill='both', expand=True, pady=10)

        # --- Profile entries (left) ---
        labels = [
            ("Registration No (reg_no)", s.reg_no, True),
            ("First Name", s.first_name, False),
            ("Last Name", s.last_name, False),
            ("Date of Birth (YYYY-MM-DD)", s.date_of_birth.isoformat(), False),
            ("Roll No", s.roll_no, False),
            ("Batch", s.batch, False),
            ("Degree", s.degree, False),
            ("Course", s.course, False),
            ("Semester", str(s.semester), False),
            ("SGPA", "" if s.sgpa is None else str(s.sgpa), True),
            ("CGPA", "" if s.cgpa is None else str(s.cgpa), True),
        ]

        self.profile_entries = {}
        for i, (label_text, value, disabled) in enumerate(labels):
            ttk.Label(left, text=label_text, foreground="#333", font=('Segoe UI', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=6)
            ent = ttk.Entry(left, width=32, font=('Segoe UI', 10))
            ent.insert(0, value)
            ent.grid(row=i, column=1, pady=6, padx=(8,0))
            if disabled:
                ent.configure(state='disabled')
            self.profile_entries[label_text] = ent

        ttk.Button(left, text="Change Password", style="Accent.TButton", command=lambda: self._prompt_change_password(force=False)).grid(row=len(labels)+1, column=0, columnspan=2, pady=(10,0))
        ttk.Button(left, text="Save Profile Changes", style="Accent.TButton", command=self._save_profile_changes).grid(row=len(labels), column=0, columnspan=2, pady=(12,0))

        # --- Student Summary (right) ---
        ttk.Label(right, text="Student Summary", font=('Segoe UI', 16, 'bold'), foreground="#2C3E50").pack(anchor='w', pady=(0,10))

        summary_frame = tk.Frame(right, bg="#ECF0F1", bd=2, relief='groove', padx=12, pady=12)
        summary_frame.pack(fill='both', expand=True)

        summary_items = [
            f"Name: {s.first_name} {s.last_name}",
            f"Registration No: {s.reg_no}",
            f"Roll No: {s.roll_no}",
            f"Batch: {s.batch}",
            f"Degree: {s.degree}",
            f"Course: {s.course}",
            f"Semester: {s.semester}",
            f"SGPA: {s.sgpa if s.sgpa is not None else 'N/A'}",
            f"CGPA: {s.cgpa if s.cgpa is not None else 'N/A'}",
        ]

        for text in summary_items:
            lbl = tk.Label(summary_frame, text=text, anchor='w', bg="#ECF0F1", font=('Segoe UI', 12))
            lbl.pack(fill='x', pady=4)


    def _save_profile_changes(self):
        try:
            s = Student.objects.get(reg_no=self.student.reg_no)
            s.first_name = self.profile_entries["First Name"].get().strip()
            s.last_name = self.profile_entries["Last Name"].get().strip()

            dob_text = self.profile_entries["Date of Birth (YYYY-MM-DD)"].get().strip()
            dob = parse_date(dob_text)
            if not dob:
                messagebox.showerror("Invalid date", "Please enter Date of Birth in YYYY-MM-DD format.")
                return
            s.date_of_birth = dob

            s.roll_no = self.profile_entries["Roll No"].get().strip()
            s.batch = self.profile_entries["Batch"].get().strip()
            s.degree = self.profile_entries["Degree"].get().strip()
            s.course = self.profile_entries["Course"].get().strip()

            semester_text = self.profile_entries["Semester"].get().strip()
            if semester_text == "":
                messagebox.showerror("Input error", "Semester cannot be empty.")
                return
            try:
                s.semester = int(semester_text)
            except ValueError:
                messagebox.showerror("Input error", "Semester must be an integer.")
                return

            s.save()
            self.student = s
            messagebox.showinfo("Saved", "Profile updated successfully.")
            self._build_profile_tab()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to save profile:\n{e}")

    # -------------------------
    # Subjects Tab
    # -------------------------
    def _build_subjects_tab(self):
        for child in self.subjects_tab.winfo_children():
            child.destroy()

        top = ttk.Frame(self.subjects_tab)
        top.pack(fill='x', pady=(0,10))
        ttk.Label(top, text="All Available Subjects", font=('Segoe UI', 12, 'bold')).pack(side='left')

        # Treeview listing subjects
        columns = ("subject_code", "subject_name", "credits", "semester")
        tree = ttk.Treeview(self.subjects_tab, columns=columns, show='headings', height=16)
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, anchor='w', width=200 if col == 'subject_name' else 100)
        tree.pack(fill='both', expand=True, padx=4, pady=6)

        # populate
        try:
            subjects = Subject.objects.all().order_by('subject_code')
            for subj in subjects:
                tree.insert('', 'end', iid=subj.subject_code, values=(subj.subject_code, subj.subject_name, subj.credits, subj.semester))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load subjects:\n{e}")
            return

        # Enroll button
        btn_frame = ttk.Frame(self.subjects_tab)
        btn_frame.pack(fill='x', pady=(8,0))
        ttk.Button(btn_frame, text="Enroll in Selected Subject", command=lambda: self._enroll_selected_subject(tree)).pack(side='left', padx=(0,8))
        ttk.Button(btn_frame, text="Refresh Subjects", command=self._build_subjects_tab).pack(side='left')

        # small help
        ttk.Label(btn_frame, text="Select a subject row and click Enroll", foreground="#444").pack(side='left', padx=(12,0))

    def _enroll_selected_subject(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a subject to enroll in.")
            return
        subject_code = sel[0]  # we used subject_code as iid
        try:
            subject = Subject.objects.get(subject_code=subject_code)
        except Subject.DoesNotExist:
            messagebox.showerror("Error", "Selected subject not found in database.")
            return

        # check if already enrolled for same semester (use subject.semester)
        try:
            exists = Enrollment.objects.filter(reg_no=self.student, subject_code=subject).exists()
            if exists:
                messagebox.showinfo("Already enrolled", f"You are already enrolled in {subject}.")
                return

            # create enrollment: use subject.semester as enrollment.semester
            enrollment = Enrollment(reg_no=self.student, subject_code=subject, semester=subject.semester)
            enrollment.save()

            # optionally create Attendance and AcademicRecord placeholders? We'll not auto-create AcademicRecord here.
            Attendance.objects.create(enrollment=enrollment, total_classes=0, attended_classes=0)
            # Do not create AcademicRecord automatically — grades will be set by admin.
            messagebox.showinfo("Enrolled", f"Successfully enrolled in {subject}.")
            # Refresh enrollments and other views
            self._build_enrollments_tab()
            self._build_attendance_tab()
            self._build_grades_tab()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to enroll:\n{e}")

    # -------------------------
    # Enrollments Tab
    # -------------------------
    def _build_enrollments_tab(self):
        for child in self.enrollments_tab.winfo_children():
            child.destroy()

        ttk.Label(self.enrollments_tab, text="Your Enrollments", font=('Segoe UI', 12, 'bold')).pack(anchor='w')

        columns = ("enrollment_id", "subject_code", "subject_name", "semester")
        tree = ttk.Treeview(self.enrollments_tab, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, anchor='w', width=200 if col == 'subject_name' else 100)
        tree.pack(fill='both', expand=True, padx=4, pady=6)

        # populate
        try:
            enrollments = Enrollment.objects.filter(reg_no=self.student).select_related('subject_code').order_by('semester')
            for e in enrollments:
                subj = e.subject_code
                tree.insert('', 'end', iid=str(e.enrollment_id), values=(e.enrollment_id, subj.subject_code, subj.subject_name, e.semester))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load enrollments:\n{e}")
            return

        btn_frame = ttk.Frame(self.enrollments_tab)
        btn_frame.pack(fill='x', pady=(8,0))

        ttk.Button(btn_frame, text="View Details", command=lambda: self._view_enrollment_details(tree)).pack(side='left', padx=(0,6))
        ttk.Button(btn_frame, text="Withdraw Selected Enrollment", command=lambda: self._withdraw_enrollment(tree)).pack(side='left', padx=(6,6))
        ttk.Button(btn_frame, text="Refresh", command=self._build_enrollments_tab).pack(side='left', padx=(6,0))

        ttk.Label(btn_frame, text="(Withdraw removes the enrollment and related attendance/record.)", foreground="#444").pack(side='left', padx=(12,0))

    def _view_enrollment_details(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an enrollment to view.")
            return
        eid = sel[0]
        try:
            enrollment = Enrollment.objects.get(enrollment_id=eid)
        except Enrollment.DoesNotExist:
            messagebox.showerror("Error", "Enrollment not found.")
            return

        subj = enrollment.subject_code
        details = [
            f"Enrollment ID: {enrollment.enrollment_id}",
            f"Subject: {subj.subject_code} - {subj.subject_name}",
            f"Semester: {enrollment.semester}",
            f"Student: {enrollment.reg_no.reg_no} - {enrollment.reg_no.first_name} {enrollment.reg_no.last_name}",
        ]

        # Attendance
        try:
            att = enrollment.attendance
            details.append(f"Attendance: {att.attended_classes}/{att.total_classes} ({att.percentage}%)")
        except Attendance.DoesNotExist:
            details.append("Attendance: No record")

        # AcademicRecord
        try:
            rec = enrollment.academic_record
            details.append(f"Grade: {rec.grade}, Credit Points: {rec.credit_points}")
        except AcademicRecord.DoesNotExist:
            details.append("Academic Record: No record")

        messagebox.showinfo("Enrollment Details", "\n".join(details))

    def _withdraw_enrollment(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an enrollment to withdraw.")
            return
        eid = sel[0]
        if not messagebox.askyesno("Confirm Withdraw", "Are you sure you want to withdraw from this subject? This will delete the enrollment and its attendance/academic record."):
            return
        try:
            enrollment = Enrollment.objects.get(enrollment_id=eid)
            # cascade delete will remove attendance and academicrecord because of on_delete
            enrollment.delete()
            messagebox.showinfo("Withdrawn", "Enrollment withdrawn successfully.")
            self._build_enrollments_tab()
            self._build_subjects_tab()
            self._build_attendance_tab()
            self._build_grades_tab()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to withdraw:\n{e}")

    # -------------------------
    # Attendance Tab (Read-only)
    # -------------------------
    def _build_attendance_tab(self):
        for child in self.attendance_tab.winfo_children():
            child.destroy()

        ttk.Label(self.attendance_tab, text="Attendance Report (Read-only)", font=('Segoe UI', 12, 'bold')).pack(anchor='w')

        columns = ("subject_code", "subject_name", "total_classes", "attended_classes", "percentage")
        tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings', height=14)
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, anchor='w', width=180 if col == 'subject_name' else 100)
        tree.pack(fill='both', expand=True, padx=4, pady=6)

        # populate
        try:
            enrollments = Enrollment.objects.filter(reg_no=self.student).select_related('subject_code').order_by('semester')
            for e in enrollments:
                subj = e.subject_code
                try:
                    att = e.attendance
                    perc = f"{att.percentage}%"
                    total = att.total_classes
                    attended = att.attended_classes
                except Attendance.DoesNotExist:
                    perc = "N/A"
                    total = "N/A"
                    attended = "N/A"
                tree.insert('', 'end', iid=str(e.enrollment_id), values=(subj.subject_code, subj.subject_name, total, attended, perc))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load attendance:\n{e}")
            return

        # optional: view details button
        btn_frame = ttk.Frame(self.attendance_tab)
        btn_frame.pack(fill='x', pady=(8,0))
        ttk.Button(btn_frame, text="View Selected Attendance Details", command=lambda: self._view_attendance_detail(tree)).pack(side='left')
        ttk.Button(btn_frame, text="Refresh", command=self._build_attendance_tab).pack(side='left', padx=(8,0))

    def _view_attendance_detail(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an enrollment to view attendance.")
            return
        eid = sel[0]
        try:
            e = Enrollment.objects.get(enrollment_id=eid)
        except Enrollment.DoesNotExist:
            messagebox.showerror("Error", "Enrollment not found.")
            return

        try:
            att = e.attendance
            details = [
                f"Subject: {e.subject_code.subject_code} - {e.subject_code.subject_name}",
                f"Total Classes: {att.total_classes}",
                f"Attended Classes: {att.attended_classes}",
                f"Attendance Percentage: {att.percentage}%",
            ]
        except Attendance.DoesNotExist:
            details = ["No attendance record available for this enrollment."]
        messagebox.showinfo("Attendance Details", "\n".join(map(str, details)))

    # -------------------------
    # Grades Tab (Read-only)
    # -------------------------
    def _build_grades_tab(self):
        for child in self.grades_tab.winfo_children():
            child.destroy()

        ttk.Label(self.grades_tab, text="Academic Records (Grades) - Read-only", font=('Segoe UI', 12, 'bold')).pack(anchor='w')

        columns = ("subject_code", "subject_name", "grade", "credit_points")
        tree = ttk.Treeview(self.grades_tab, columns=columns, show='headings', height=14)
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, anchor='w', width=180 if col == 'subject_name' else 120)
        tree.pack(fill='both', expand=True, padx=4, pady=6)

        try:
            enrollments = Enrollment.objects.filter(reg_no=self.student).select_related('subject_code').order_by('semester')
            for e in enrollments:
                subj = e.subject_code
                try:
                    rec = e.academic_record
                    grade = rec.grade
                    cp = rec.credit_points
                except AcademicRecord.DoesNotExist:
                    grade = "N/A"
                    cp = "N/A"
                tree.insert('', 'end', iid=str(e.enrollment_id), values=(subj.subject_code, subj.subject_name, grade, cp))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load grades:\n{e}")
            return

        btn_frame = ttk.Frame(self.grades_tab)
        btn_frame.pack(fill='x', pady=(8,0))
        ttk.Button(btn_frame, text="View Grade Details", command=lambda: self._view_grade_detail(tree)).pack(side='left')
        ttk.Button(btn_frame, text="Refresh", command=self._build_grades_tab).pack(side='left', padx=(8,0))

    def _view_grade_detail(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select an enrollment to view grade.")
            return
        eid = sel[0]
        try:
            e = Enrollment.objects.get(enrollment_id=eid)
        except Enrollment.DoesNotExist:
            messagebox.showerror("Error", "Enrollment not found.")
            return

        try:
            rec = e.academic_record
            details = [
                f"Subject: {e.subject_code.subject_code} - {e.subject_code.subject_name}",
                f"Grade: {rec.grade}",
                f"Credit Points: {rec.credit_points}",
            ]
        except AcademicRecord.DoesNotExist:
            details = ["No academic record available for this enrollment."]
        messagebox.showinfo("Grade Details", "\n".join(map(str, details)))

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app = SISApp()
    app.mainloop()
