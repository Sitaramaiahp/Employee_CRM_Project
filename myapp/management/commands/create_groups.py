
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import Employee, Attendance, ActivityLog

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        hr_group, _ = Group.objects.get_or_create(name='HR Manager')
        emp_group, _ = Group.objects.get_or_create(name='Employee')

        # Get content types
        emp_ct = ContentType.objects.get_for_model(Employee)
        att_ct = ContentType.objects.get_for_model(Attendance)
        log_ct = ContentType.objects.get_for_model(ActivityLog)

        # HR Manager permissions
        hr_permissions = Permission.objects.filter(
            content_type__in=[emp_ct, att_ct, log_ct],
            codename__in=[
                'add_employee', 'change_employee', 'delete_employee', 'view_employee',
                'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance',
                'view_activitylog'
            ]
        )
        hr_group.permissions.set(hr_permissions)

        # Employee permissions — limited to profile & own attendance
        emp_permissions = Permission.objects.filter(
            content_type__in=[emp_ct, att_ct],
            codename__in=[
                'change_employee', 'view_employee',
                'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance'
            ]
        )
        emp_group.permissions.set(emp_permissions)

        self.stdout.write(self.style.SUCCESS("Groups and permissions created successfully."))
