from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Customize admin site header and title
admin.site.site_header = "Student Information System"
admin.site.site_title = "SIS Admin Portal"
admin.site.index_title = "Welcome to Student Information System"