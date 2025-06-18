
from django import forms
from .models import Employee
from django.contrib.auth.models import User
from .models import Attendance

# Signup Form
class SignupForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# Employees Form
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'user' : forms.HiddenInput(),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'department': forms.Select(),
            'role': forms.Select(),
        }

# Attendance Form
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in', 'check_out']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
        }
