from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Department, Role, CustomUser
from django.contrib.auth.models import Group, Permission

# Форма для модели Department
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название отдела',
                'required': True
            }),
        }


# Форма для модели Role
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название отдела',
                'required': True
            }),
        }


# Форма для модели User
class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'middle_name', 'is_admin', 'department', 'role', 'email', 'status']

    def save(self, commit=True):
        user = super().save(commit=False)

        # Assign admin rights if is_admin is True
        if user.is_admin:
            # Add the user to the 'Admin' group (if you have such a group)
            admin_group, created = Group.objects.get_or_create(name='Admin')
            user.groups.add(admin_group)

            # Grant all permissions to the user (if required)
            permissions = Permission.objects.all()
            user.user_permissions.set(permissions)

            user.is_staff = True
            user.is_superuser = True

        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'middle_name', 'is_admin', 'department', 'role', 'email', 'status']

    def save(self, commit=True):
        user = super().save(commit=False)

        # Ensure admin rights are updated if is_admin changes
        if user.is_admin:
            # Add the user to the 'Admin' group (if you have such a group)
            admin_group, created = Group.objects.get_or_create(name='Admin')
            user.groups.add(admin_group)

            # Grant all permissions to the user (if required)
            permissions = Permission.objects.all()
            user.user_permissions.set(permissions)

            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
            user.groups.clear()
            user.user_permissions.clear()

        if commit:
            user.save()
        return user
