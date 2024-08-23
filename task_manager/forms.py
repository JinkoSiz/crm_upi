from django import forms
from .models import Department, Role

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