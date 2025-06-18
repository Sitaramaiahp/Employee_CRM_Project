
from django.urls import path
from .import views

urlpatterns = [
    path('', views.employee_list, name="employee_list"),
    path('add/', views.add_employee, name='add_employee'),
    path('edit/<str:id>/', views.edit_employee, name='edit_employee'),
    path('delete/<str:id>/', views.delete_employee, name='delete_employee'),
    path('alldelete-emp/', views.alldelete_employee, name="alldelete_employee"),
    path('profile/', views.employee_profile, name='employee_profile'),
    path('attendance-list/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/edit/<str:id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/delete/<str:id>/', views.delete_attendance, name='delete_attendance'),
    path('alldelete-atd/', views.alldelete_attendance, name="alldelete_attendence"),
    path('my-attendance/', views.employee_attendance_list, name='employee_attendance_list'),
    path('activity-log/', views.activity_log, name='activity_log'),
]