from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'role', 'status', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('position', 'department', 'role', 'status', 'foto')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
