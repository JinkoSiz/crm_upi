from django.urls import path
from . import views

urlpatterns = [
    # Отделы
    path('departments/', views.department, name='department-list'),
    path('departments/create/', views.createDepartment, name='department-create'),
    path('departments/<uuid:pk>/edit/', views.updateDepartment, name='department-edit'),
    path('departments/<uuid:pk>/delete/', views.deleteDepartment, name='department-delete'),
    
    # Должности
    path('roles/', views.role, name='role-list'),
    path('roles/create/', views.createRole, name='role-create'),
    path('roles/<uuid:pk>/edit/', views.updateRole, name='role-edit'),
    path('roles/<uuid:pk>/delete/', views.deleteRole, name='role-delete'),
]
