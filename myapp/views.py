from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee, Attendance, ActivityLog
from .forms import SignupForm, EmployeeForm, AttendanceForm
from datetime import date, datetime

# Permissions
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

def is_hr(user):
    return user.groups.filter(name='HR Manager').exists()

def is_employee(user):
    return user.groups.filter(name='Employee').exists()

# Signup
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Add user to "Employee" group
            employee_group, created = Group.objects.get_or_create(name='Employee')
            user.groups.add(employee_group)

            # Create basic Employee profile
            Employee.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                role='Employee',
                join_date=date.today()
                # other fields left null
            )

            # Login and redirect to own profile
            login(request, user)
            return redirect('employee_profile')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form' : form})

# login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect based on group
            if user.groups.filter(name='Employee').exists():
                return redirect('employee_profile')  # send to own profile
            else:
                return redirect('employee_list')  # send to admin/HR dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form' : form})

# Logout
def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

# Create or Add Employee
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = request.user
            employee.save()
            ActivityLog.objects.create(
                user=request.user,
                action="Created Employee",
                description=f"Added employee: {form.cleaned_data['name']}"
            )
            return redirect('employee_list')
    else:
        form = EmployeeForm(initial={'user' : request.user})
    return render(request, 'employee_form.html', {'form': form, 'title': 'Add Employee'})

# Read / List Employees
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def employee_list(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    role_filter = request.GET.get('role', '')
    employees = Employee.objects.all()
    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) | Q(email__icontains=search_query)
        )
    if department_filter:
        employees = employees.filter(department=department_filter)
    if role_filter:
        employees = employees.filter(role=role_filter)
    else:
        employees = Employee.objects.all().order_by('id')
        paginator = Paginator(employees, 5)  # 5 per page
        page = request.GET.get('page')
        employees = paginator.get_page(page)
    
    context = {
        'employees': employees,
        'departments': Employee.objects.values_list('department', flat=True).distinct(),
        'roles': Employee.objects.values_list('role', flat=True).distinct(),
        'search_query': search_query,
        'selected_department': department_filter,
        'selected_role': role_filter,
    }

    return render(request, 'employee_list.html', context)

# Update Employee
@login_required
def edit_employee(request, id):
    employee = Employee.objects.get(id=id)
    name = employee.name
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = request.user
            employee.save()
            ActivityLog.objects.create(
                user=request.user,
                action="Updated Employee",
                description=f"Updated employee: {name} - {form.cleaned_data['name']}"
            )
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee,initial={'user' : request.user})
    return render(request, 'employee_form.html', {'form': form, "employee" : employee, 'title': 'Update Employee'})

# Delete Employee
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def delete_employee(request, id):
    employee = Employee.objects.get(id=id)
    if request.method == 'POST':
        ActivityLog.objects.create(
            user=request.user,
            action="Deleted Employee",
            description=f"Deleted employee: {employee.name}"
        )
        employee.delete()
        return redirect('employee_list')
    return render(request, 'confirm_delete.html', {'employee': employee})

# All Delete Employee
@login_required
@user_passes_test(lambda u: is_admin(u))
def alldelete_employee(request):
    employee = Employee.objects.all()
    if request.method == "POST":
        ActivityLog.objects.create(
            user=request.user,
            action="Deleted Employee",
            description=f"Deleted employees : All"
        )
        employee.delete()
        return redirect("employee_list")
    return render(request, 'confirm_delete.html', {"msg" : "ALL"})

# Employee Profile
@login_required
def employee_profile(request):
    try:
        employee = Employee.objects.get(user=request.user)
        return render(request, 'employee_profile.html', {'employee' : employee})
    except Employee.DoesNotExist:
        return HttpResponse("Employee Profile not Found")

# CREATE Attendance
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def add_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="Added Attendance",
                description=f"Added Attendance: {form.cleaned_data['employee']}"
            )
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'attendance_form.html', {'form': form, 'title': 'Add Attendance'})

# READ Attendance List
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def attendance_list(request):
    query = request.GET.get('q')         # employee name search
    date_filter = request.GET.get('date')  # specific date
    records = Attendance.objects.all().select_related('employee')
    if query:
        records = records.filter(employee__name__icontains=query)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            records = records.filter(date=date_obj)
        except ValueError:
            pass

    records = records.order_by('-date')
     # Pagination
    paginator = Paginator(records, 10)  # Show 10 records per page
    page = request.GET.get('page')
    records = paginator.get_page(page)
    return render(request, 'attendance_list.html', {'records': records})

# UPDATE Attendance
@login_required
def edit_attendance(request, id):
    record = Attendance.objects.get(id=id)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="Updated Attendance",
                description=f"Updated Attendance: {form.cleaned_data['employee']}"
            )
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=record)
    return render(request, 'attendance_form.html', {'form': form, 'title': 'Edit Attendance'})

# DELETE Attendance
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def delete_attendance(request, id):
    record = Attendance.objects.get(id=id)
    if request.method == 'POST':
        ActivityLog.objects.create(
            user=request.user,
            action="Deleted Attendance",
            description=f"Deleted Attendance: {record.name}"
        )
        record.delete()
        return redirect('attendance_list')
    return render(request, 'confirm_delete.html', {'record': record})

# All Delete
@login_required
@user_passes_test(lambda u: is_admin(u))
def alldelete_attendance(request):
    record = Attendance.objects.all()
    if request.method == "POST":
        ActivityLog.objects.create(
            user=request.user,
            action="Deleted Attendance",
            description=f"Deleted Attendance: All"
        )
        record.delete()
        return redirect("employee_list")
    return render(request, 'confirm_delete.html', {"msg" : "ALL"})

# Employee Attendance
@login_required
def employee_attendance_list(request):
    # Get the Employee profile for the logged-in user
    employee = Employee.objects.get(user=request.user)
    
    # Filter attendance records for that employee
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    
    return render(request, 'employee_attendance.html', {'attendances': attendances})

# Activity Log
@login_required
@user_passes_test(lambda u: is_admin(u) or is_hr(u))
def activity_log(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'activity_log.html', {'logs': logs})

