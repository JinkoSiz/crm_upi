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
    path('users/check_user_exists/', views.check_user_exists, name='check-user-exists'),
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

    # Разделы
    path('sections/', views.section, name='section-list'),
    path('sections/create/', views.createSection, name='section-create'),
    path('sections/<uuid:pk>/edit/', views.updateSection, name='section-edit'),
    path('sections/<uuid:pk>/delete/', views.deleteSection, name='section-delete'),
    
    # Марки
    path('marks/', views.mark, name='mark-list'),
    path('marks/create/', views.createMark, name='mark-create'),
    path('marks/<uuid:pk>/edit/', views.updateMark, name='mark-edit'),
    path('marks/<uuid:pk>/delete/', views.deleteMark, name='mark-delete'),

    # Задачи
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/create/', views.create_task, name='task-create'),
    path('tasks/<uuid:pk>/edit/', views.update_task, name='task-edit'),
    path('tasks/<uuid:pk>/delete/', views.delete_task, name='task-delete'),

    # Логи времени
    path('timelogs/', views.timelog_list, name='timelog-list'),
    path('timelog/create/', views.timelog_create, name='timelog-create'),
    path('timelog/<str:pk>/edit/', views.timelog_update, name='timelog-update'),
    path('timelog/<str:pk>/delete/', views.timelog_delete, name='timelog-delete'),

    # Основная страница
    path('', views.user_dashboard, name='user-dashboard'),

    # Отчеты
    path('reports/', views.reports_view, name='reports'),
    path('reports-employees/', views.reports_employees, name='reports-employees'),
    path('report/create/', views.report_create, name='report_create'),
    path('reset-session/', views.reset_session, name='reset-session'),
    path('final-report/', views.final_report, name='final-report'),
    path('get-buildings/', views.get_buildings, name='get-buildings'),
    path('get_buildings_for_project/<int:project_id>/', views.get_buildings_for_project, name='get_buildings_for_project'),
    path('get-sections/', views.get_sections, name='get-sections'),

    # Экспорт в эксель
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
    path('export-to-excel-employees/', views.export_reports_employees_excel, name='export_reports_employees_excel'),
    path('export-to-excel-project/', views.export_reports_view_excel, name='export_reports_view_excel'),

]
