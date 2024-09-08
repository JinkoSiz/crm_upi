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
    
    # Пользователи
    path('users/', views.user, name='user-list'),
    path('users/create/', views.createUser, name='user-create'),
    path('users/<uuid:pk>/edit/', views.updateUser, name='user-edit'),
    path('users/<uuid:pk>/delete/', views.deleteUser, name='user-delete'),
    path('users/<uuid:pk>/invite/', views.send_invitation, name='send-invitation'),
    path('users/<uuid:pk>/reset-password', views.reset_password, name='reset-password'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Проекты
    path('projects/', views.project, name='project-list'),
    path('projects/<uuid:pk>/', views.project_detail, name='project-detail'),
    path('projects/create/', views.createProject, name='project-create'),
    path('projects/<uuid:pk>/edit/', views.updateProject, name='project-update'),
    path('projects/<uuid:pk>/delete/', views.deleteProject, name='project-delete'),
    path('buildings/create/', views.building_create, name='building-create'),
    path('buildings/<uuid:building_id>/delete/', views.building_delete, name='building-delete'),

    # ProjectBuilding
    path('projects/<uuid:project_pk>/buildings/add/', views.project_building_create, name='project_building-create'),
    path('project_buildings/<uuid:pk>/delete/', views.project_building_delete, name='project_building-delete'),

    # ProjectSection
    path('projects/<uuid:project_pk>/sections/add/', views.project_section_create, name='project_section-create'),
    path('project_sections/<uuid:pk>/delete/', views.project_section_delete, name='project_section-delete'),
]
