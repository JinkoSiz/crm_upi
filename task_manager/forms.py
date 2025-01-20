from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import *
from django.contrib.auth.models import Group, Permission


# Форма для модели Department
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['title']
        labels = {
            'title': 'Название',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название отдела',
                'required': True
            }),
        }


# Форма для модели Role
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['title']
        labels = {
            'title': 'Название'
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название должности',
                'required': True
            }),
        }


class CustomUserCreationForm(forms.ModelForm):
    full_name = forms.CharField(label='ФИО', max_length=255)
    is_admin = forms.ChoiceField(choices=[(False, 'Пользователь'), (True, 'Админ')], label="Роль")

    class Meta:
        model = CustomUser

        fields = ['full_name', 'role', 'department', 'is_admin', 'email']

        labels = {
            'full_name': 'ФИО',
            'role': 'Должность',
            'department': 'Отдел',
            'is_admin': 'Роль',
            'email': 'Email'
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        # Разбиваем full_name на три части: фамилия, имя, отчество
        full_name = self.cleaned_data['full_name']
        name_parts = full_name.split()
        
        if len(name_parts) == 3:
            user.last_name = name_parts[0]  # Фамилия
            user.first_name = name_parts[1]  # Имя
            user.middle_name = name_parts[2]  # Отчество
        elif len(name_parts) == 2:
            user.last_name = name_parts[0]
            user.first_name = name_parts[1]
            user.middle_name = ''  # Если отчество не указано
        else:
            user.first_name = full_name  # Если только одно имя

        # Обрабатываем роль пользователя
        is_admin = self.cleaned_data.get('is_admin')
        if(is_admin == 'False'):
            user.is_admin = False
        else:
            user.is_admin = True

        if not user.username:
            user.username = get_random_string(8)

        if commit:
            user.save()

            # Если пользователь - админ, добавляем группу
            if user.is_admin:
                admin_group, created = Group.objects.get_or_create(name='Admin')
                user.groups.add(admin_group)
                permissions = Permission.objects.all()
                user.user_permissions.set(permissions)
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
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


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'status']


class ProjectBuildingForm(forms.ModelForm):
    class Meta:
        model = ProjectBuilding
        fields = ['project', 'building']


class ProjectSectionForm(forms.ModelForm):
    class Meta:
        model = ProjectSection
        fields = ['project', 'section']


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title']
        labels = {
            'title': 'Название',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название раздела',
                'required': True
            }),
        }


# Форма для модели Mark
class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['title']
        labels = {
            'title': 'Название',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название марки',
                'required': True
            }),
        }


# Форма для модели TaskType
class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = ['title']
        labels = {
            'title': 'Название',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название задачи',
                'required': True
            }),
        }


# Форма для модели TimeLog
class TimelogForm(forms.ModelForm):
    class Meta:
        model = Timelog
        fields = ['project', 'stage', 'section', 'building', 'mark', 'task', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }