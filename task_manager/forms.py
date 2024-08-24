from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Department, Role, CustomUser

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
        fields = ['first_name', 'last_name', 'middle_name', 'department', 'role', 'email', 'status']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Generate a random username and ensure it's unique
        username = get_random_string(8)
        while CustomUser.objects.filter(username=username).exists():
            username = get_random_string(8)
        user.username = username
        
        # Generate a random password
        password = get_random_string(8)
        user.set_password(password)
        
        if commit:
            user.save()
            # Send the email with the login credentials
            send_mail(
                'Invitation to join',
                f'You have been invited to join. Your login credentials are:\nUsername: {user.username}\nPassword: {password}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
        return user


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'middle_name', 'department', 'role', 'email', 'status']
