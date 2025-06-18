
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Employee Table
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to Django user
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)
    department = models.CharField(max_length=100, choices=[
    ('IT', 'IT'),('HR', 'HR'),('Sales', 'Sales'),('Finance', 'Finance'),
    ])
    role = models.CharField(max_length=100, choices=[
    ('Software Engineer', 'Software Engineer'),
    ('HR Manager', 'HR Manager'),
    ('Sales Executive', 'Sales Executive'),
    ('Accountant', 'Accountant'),
    ])
    join_date = models.DateField()
    image = models.ImageField(upload_to='employee_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.department}"
    
# Attendance Table
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

# Activitylog Table
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"