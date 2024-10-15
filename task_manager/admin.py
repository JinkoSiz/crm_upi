from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'role', 'status', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin', 'department', 'role', 'status', 'foto')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Проекты
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Здания
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Проект-Здание
@admin.register(ProjectBuilding)
class ProjectBuildingAdmin(admin.ModelAdmin):
    list_display = ('project', 'building', 'created_at', 'updated_at')
    search_fields = ('project__title', 'building__title')
    readonly_fields = ('created_at', 'updated_at')


# Проект-Раздел
@admin.register(ProjectSection)
class ProjectSectionAdmin(admin.ModelAdmin):
    list_display = ('project', 'section', 'created_at', 'updated_at')
    search_fields = ('project__title', 'section__title')
    readonly_fields = ('created_at', 'updated_at')


# Разделы
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Марки
@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Задачи
@admin.register(TaskType)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')


# Тайм Логи
@admin.register(Timelog)
class TimelogAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'project', 'stage', 'date', 'time')
    search_fields = ('user__username', 'project__title', 'stage')
    list_filter = ('stage', 'department', 'project', 'mark', 'task')
    ordering = ('-date',)
    date_hierarchy = 'date'