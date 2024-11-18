from datetime import timedelta, datetime
import re
import dateparser

import openpyxl
from django.utils.dateparse import parse_date
from openpyxl.styles import PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl import Workbook
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models.functions import Concat
from django.db.models import F, Value
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import *
from django.db.models import Q, Sum
from django.utils import timezone
from dateutil import parser


def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_authenticated and u.is_admin, login_url=login_url)


# Отделы
@admin_required(login_url='login')
def department(request):
    # Попробуем получить отделы из кэша
    departmentObj = cache.get('department_list')
    if not departmentObj:
        # Если кэш пуст, загружаем данные из базы и кэшируем
        departmentObj = Department.objects.all()
        cache.set('department_list', departmentObj, timeout=60 * 15)  # Кэшируем на 15 минут

    form = DepartmentForm()
    return render(request, 'task_manager/departments_list.html', {'departments': departmentObj, 'form': form})


def createDepartment(request):
    form = DepartmentForm()

    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            cache.delete('department_list')  # Удаляем кэш после создания
            return redirect('department-list')

    context = {'form': form}
    return render(request, 'task_manager/department_form.html', context)


def updateDepartment(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(instance=department)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            department = form.save()
            cache.delete('department_list')  # Удаляем кэш после обновления
            return redirect('department-list')

    context = {'form': form, 'department': department}
    return render(request, 'task_manager/department_form.html', context)


def deleteDepartment(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        cache.delete('department_list')  # Удаляем кэш после удаления
        return redirect('department-list')

    context = {'object': department}
    return render(request, 'task_manager/department_form.html', context)


# Должности
@admin_required(login_url='login')
def role(request):
    # Пробуем получить список ролей из кэша
    roleObj = cache.get('role_list')

    if not roleObj:
        roleObj = Role.objects.all()
        cache.set('role_list', roleObj, 600)  # Кэшируем на 10 минут (600 секунд)

    form = RoleForm()
    return render(request, 'task_manager/roles_list.html', {'roles': roleObj, 'form': form})


def createRole(request):
    form = RoleForm()

    if request.method == 'POST':
        form = RoleForm(request.POST, request.FILES)
        if form.is_valid():
            role = form.save(commit=False)
            role.save()

            # Сбрасываем кэш списка ролей
            cache.delete('role_list')

            return redirect('role-list')

    context = {'form': form}
    return render(request, 'task_manager/role_form.html', context)


def updateRole(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(instance=role)

    if request.method == 'POST':
        form = RoleForm(request.POST, request.FILES, instance=role)
        if form.is_valid():
            role = form.save()

            # Сбрасываем кэш списка ролей
            cache.delete('role_list')

            return redirect('role-list')

    context = {'form': form, 'role': role}
    return render(request, 'task_manager/role_form.html', context)


def deleteRole(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()

        # Сбрасываем кэш списка ролей
        cache.delete('role_list')

        return redirect('role-list')

    context = {'object': role}
    return render(request, 'task_manager/role_form.html', context)


# Юзеры
@admin_required(login_url='login')
def user(request):
    # Кэшируем списки отделов и ролей, чтобы избежать избыточных запросов
    departments = cache.get_or_set('departments_cache', Department.objects.all(), timeout=60 * 15)
    roles = cache.get_or_set('roles_cache', Role.objects.all(), timeout=60 * 15)

    # Применяем фильтры, если они есть
    filters = Q()
    if request.GET.get('status'):
        filters &= Q(status=request.GET.get('status'))
    if request.GET.get('department'):
        filters &= Q(department__id=request.GET.get('department'))
    if request.GET.get('role'):
        filters &= Q(role__id=request.GET.get('role'))
    if request.GET.get('last_name'):
        filters &= Q(last_name__icontains=request.GET.get('last_name'))

    # Применяем кэширование только для полного списка пользователей без фильтров
    if filters:
        # Если есть фильтры, применяем их напрямую
        users = CustomUser.objects.select_related('department', 'role').filter(filters)
    else:
        # Используем кэш для полного списка пользователей без фильтров
        users = cache.get('user_list')
        if not users:
            users = CustomUser.objects.select_related('department', 'role').all()
            cache.set('user_list', users, timeout=60 * 5)

    form = CustomUserCreationForm()

    return render(request, 'task_manager/users_list.html', {
        'users': users,
        'form': form,
        'departments': departments,
        'roles': roles
    })


def createUser(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Очищаем кэш списка пользователей и отделов/ролей
            cache.delete('user_list')
            cache.delete('departments_cache')
            cache.delete('roles_cache')

            return redirect('user-list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'task_manager/user_form.html', {'form': form})


def updateUser(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            # Очищаем кэш после обновления пользователя
            cache.delete('user_list')
            cache.delete('departments_cache')
            cache.delete('roles_cache')

            return redirect('user-list')
    else:
        form = CustomUserChangeForm(instance=user)

    context = {'form': form, 'user': user}
    return render(request, 'task_manager/user_form.html', context)


def deleteUser(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()

        # Очищаем кэш после удаления пользователя
        cache.delete('user_list')
        cache.delete('departments_cache')
        cache.delete('roles_cache')

        return redirect('user-list')

    return render(request, 'task_manager/user_confirm_delete.html', {'user': user})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Если пользователь пригашен и входит впервые, меняем статус на активный
            if user.status == 'invited':
                user.status = 'active'
                print(user.status)
                user.save()
                print(user.status)
                # Очищаем кэш после обновления пользователя
                cache.delete('user_list')
                
            return redirect('user-dashboard')  # Redirect to your desired page after login
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'task_manager/login.html')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


def send_invitation(request, pk):
    # Выводим для отладки
    # print(f"Received pk from URL: {pk}")
    # print(f"Logged in user pk: {request.user.pk}")
    user = get_object_or_404(CustomUser, pk=pk)
    #print(f'invite: before {user.status}')
    if user.status != 'invited' and user.status != 'active':
        # Генерация случайного логина
        username = get_random_string(length=8)
        while CustomUser.objects.filter(username=username).exists():
            username = get_random_string(length=8)
        user.username = username

        # Генерация случайного пароля
        password = get_random_string(length=8)
        user.set_password(password)
        user.status = 'invited'
        user.save()
        
        # Очищаем кэш после обновления пользователя
        cache.delete('user_list')

        #print(f'invite: after {user.status}')

        # Синхронная отправка email
        send_mail(
            'Приглашение на платформу Task Manager',
            f'Ваши учетные данные для входа:\nЛогин: {user.username}\nПароль: {password}',
            'info@demotimetracker.ru',
            [user.email],
            fail_silently=False,
        )

        print('Приглашение отправлено успешно.')

        messages.success(request, 'Приглашение отправлено успешно.')
    else:
        messages.warning(request, 'Этот пользователь уже был приглашен ранее.')

    return redirect('user-list')


def reset_password(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    # Генерация нового случайного пароля
    new_password = get_random_string(length=8)
    user.set_password(new_password)
    user.save()

    # Отправка нового пароля на email пользователя
    send_mail(
        'Ваш новый пароль',
        f'Ваш новый пароль: {new_password}',
        'noreply@taskmanager.com',  # Укажите email отправителя
        [user.email],
        fail_silently=False,
    )

    messages.success(request, 'Пароль успешно сброшен и отправлен на email пользователя.')
    return redirect('user-list')


# Проекты

@admin_required(login_url='login')
def project(request):
    # Кэшируем проекты и связанные данные
    projects = cache.get_or_set(
        'projects_cache',
        Project.objects.select_related('status').prefetch_related('project_buildings__building',
                                                                  'project_sections__section'),
        timeout=60 * 15  # Кэш на 15 минут
    )

    project_status = cache.get_or_set(
        'project_status_cache',
        ProjectStatus.objects.all(),
        timeout=60 * 15
    )

    sections = cache.get_or_set(
        'sections_cache',
        Section.objects.all(),
        timeout=60 * 15
    )

    form = ProjectForm()

    return render(request, 'task_manager/project_list.html', {
        'projects': projects,
        'project_status': project_status,
        'sections': sections,
        'form': form
    })


def project_detail(request, pk):
    try:
        cache_key = f'project_detail_{pk}'
        project_data = cache.get(cache_key)

        if not project_data:
            project = Project.objects.prefetch_related(
                'project_buildings__building',
                'project_sections__section'
            ).get(pk=pk)

            buildings = [
                {
                    'building__pk': building['building__pk'],
                    'building__title': building['building__title'].strip()  # Remove extra whitespace or newlines
                }
                for building in project.project_buildings.values('building__pk', 'building__title')
            ]

            sections = [
                {
                    'section__pk': section['section__pk'],
                    'section__title': section['section__title']
                }
                for section in project.project_sections.values('section__pk', 'section__title')
            ]

            project_data = {
                'project': {
                    'title': project.title,
                    'status': str(project.status_id)  # Ensure UUID is serialized as a string
                },
                'buildings': buildings,
                'sections': sections
            }
            cache.set(cache_key, project_data, timeout=60 * 15)

        return JsonResponse(project_data)

    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def createProject(request):
    if request.method == 'POST':
        title = request.POST['title']
        status_id = request.POST['status']
        sections = request.POST.getlist('sections[]')

        with transaction.atomic():
            project = Project.objects.create(title=title, status_id=status_id)

            # Обработка зданий
            buildings = request.POST.getlist('buildings[]')
            for building_title in buildings:
                building, created = Building.objects.get_or_create(title=building_title)
                ProjectBuilding.objects.create(project=project, building=building)

            # Добавляем выбранные разделы к проекту
            for section_id in sections:
                section = Section.objects.get(pk=section_id)
                ProjectSection.objects.create(project=project, section=section)

            # Очищаем кэш после добавления проекта
            cache.delete('projects_cache')
            cache.delete('project_status_cache')
            cache.delete('sections_cache')

        return JsonResponse({'message': 'Проект создан'})


def updateProject(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)

        with transaction.atomic():
            # Обновляем название и статус проекта
            project.title = request.POST['title']
            project.status_id = request.POST['status']
            project.save()

            # Обработка зданий
            buildings = request.POST.getlist('buildings[]')
            ProjectBuilding.objects.filter(project=project).delete()
            for building_title in buildings:
                building, created = Building.objects.get_or_create(title=building_title)
                ProjectBuilding.objects.create(project=project, building=building)

            # Удаление зданий
            removed_buildings = request.POST.getlist('removed_buildings[]')
            for building_id in removed_buildings:
                try:
                    project_building = ProjectBuilding.objects.get(project=project, building_id=building_id)
                    project_building.delete()

                    # Удаляем само здание, если оно не связано с другими проектами
                    building = Building.objects.get(pk=building_id)
                    if not ProjectBuilding.objects.filter(building=building).exists():
                        building.delete()
                except ProjectBuilding.DoesNotExist:
                    continue

            # Обработка разделов
            sections = request.POST.getlist('sections[]')
            ProjectSection.objects.filter(project=project).delete()
            for section_id in sections:
                section = Section.objects.get(pk=section_id)
                ProjectSection.objects.create(project=project, section=section)

            # Очищаем кэш после обновления проекта
            cache.delete('projects_cache')
            cache.delete(f'project_detail_{pk}')
            cache.delete('project_status_cache')
            cache.delete('sections_cache')

        return JsonResponse({'message': 'Проект обновлен'})


def deleteProject(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.delete()

        # Очищаем кэш после удаления проекта
        cache.delete('projects_cache')
        cache.delete(f'project_detail_{pk}')
        cache.delete('project_status_cache')
        cache.delete('sections_cache')

        return JsonResponse({'message': 'Проект удален'})


# ProjectBuilding

def project_building_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectBuildingForm(request.POST)
        if form.is_valid():
            project_building = form.save(commit=False)
            project_building.project = project
            project_building.save()
            return redirect('project-detail', pk=project_pk)
    else:
        form = ProjectBuildingForm()
    return render(request, 'task_manager/project_building_form.html', {'form': form, 'project': project})


def project_building_delete(request, pk):
    project_building = get_object_or_404(ProjectBuilding, pk=pk)
    project_pk = project_building.project.pk
    if request.method == 'POST':
        project_building.delete()
        return redirect('project-detail', pk=project_pk)
    return render(request, 'task_manager/project_building_confirm_delete.html', {'project_building': project_building})


# ProjectSection

def project_section_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectSectionForm(request.POST)
        if form.is_valid():
            project_section = form.save(commit=False)
            project_section.project = project
            project_section.save()
            return redirect('project-detail', pk=project_pk)
    else:
        form = ProjectSectionForm()
    return render(request, 'task_manager/project_section_form.html', {'form': form, 'project': project})


def project_section_delete(request, pk):
    project_section = get_object_or_404(ProjectSection, pk=pk)
    project_pk = project_section.project.pk
    if request.method == 'POST':
        project_section.delete()
        return redirect('project-detail', pk=project_pk)
    return render(request, 'task_manager/project_section_confirm_delete.html', {'project_section': project_section})


def building_create(request):
    if request.method == 'POST':
        building_title = request.POST.get('title')
        project_id = request.POST.get('project_id')

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        try:
            building, created = Building.objects.get_or_create(title=building_title)

            if ProjectBuilding.objects.filter(project=project, building=building).exists():
                return JsonResponse({'error': 'Building already exists in this project'}, status=400)

            ProjectBuilding.objects.create(project=project, building=building)
        except IntegrityError:
            return JsonResponse({'error': 'Building with this name already exists'}, status=400)

        return JsonResponse({'message': 'Building created and added to project'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def building_delete(request, building_id):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')

        # Удаление связи между проектом и зданием
        try:
            project_building = get_object_or_404(ProjectBuilding, building_id=building_id, project_id=project_id)
            project_building.delete()

            # Теперь удаляем само здание, если оно не связано с другими проектами
            building = get_object_or_404(Building, pk=building_id)
            # Проверяем, связано ли здание с другими проектами
            if not ProjectBuilding.objects.filter(building=building).exists():
                building.delete()

            return JsonResponse({'message': 'Building removed from project and deleted'})
        except Exception as e:
            return JsonResponse({'error': 'Error deleting building: ' + str(e)}, status=400)


# Разделы
@admin_required(login_url='login')
def section(request):
    sections = Section.objects.all()
    available_marks = Mark.objects.all()  # Получаем все доступные марки
    form = SectionForm()

    return render(request, 'task_manager/sections_list.html', {
        'sections': sections,
        'form': form,
        'available_marks': available_marks  # Передаем доступные марки в контекст
    })


def createSection(request):
    form = SectionForm()

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            cache.delete('sections_cache')
            return redirect('section-list')

    return render(request, 'task_manager/section_form.html', {'form': form})


def updateSection(request, pk):
    section = get_object_or_404(Section, pk=pk)
    available_marks = Mark.objects.all()  # Все доступные марки
    section_marks = SectionMark.objects.filter(section=section)  # Марки, связанные с секцией

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            cache.delete('sections_cache')

            # Обновляем марки для секции
            marks = request.POST.getlist('marks')  # Получаем выбранные ID марок из формы
            SectionMark.objects.filter(section=section).delete()  # Удаляем старые марки

            for mark_id in marks:
                mark = Mark.objects.get(id=mark_id)
                SectionMark.objects.create(section=section, mark=mark)  # Создаем новые связи

            return redirect('section-list')
    else:
        form = SectionForm(instance=section)

    return render(request, 'task_manager/section_form.html', {
        'form': form,
        'section': section,
        'available_marks': available_marks,
        'section_marks': section_marks,
    })


def deleteSection(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == 'POST': 
        section.delete()
        cache.delete('sections_cache')
        return redirect('section-list')

    return render(request, 'task_manager/section_confirm_delete.html', {'section': section})


# Марки
@login_required(login_url='login')
def mark(request):
    # Попробуем получить марки из кэша
    marks = cache.get('mark_list')
    if not marks:
        # Если кэш пуст, загружаем данные из базы и кэшируем
        marks = Mark.objects.all()
        cache.set('mark_list', marks, timeout=60 * 15)  # Кэшируем на 15 минут

    form = MarkForm()
    return render(request, 'task_manager/mark_list.html', {'marks': marks, 'form': form})


def createMark(request):
    form = MarkForm()

    if request.method == 'POST':
        form = MarkForm(request.POST)
        if form.is_valid():
            mark = form.save(commit=False)
            mark.save()
            cache.delete('mark_list')  # Удаляем кэш после создания
            return redirect('mark-list')

    context = {'form': form}
    return render(request, 'task_manager/mark_form.html', context)


def updateMark(request, pk):
    mark = get_object_or_404(Mark, pk=pk)
    form = MarkForm(instance=mark)

    if request.method == 'POST':
        form = MarkForm(request.POST, instance=mark)
        if form.is_valid():
            mark = form.save()
            cache.delete('mark_list')  # Удаляем кэш после обновления
            return redirect('mark-list')

    context = {'form': form, 'mark': mark}
    return render(request, 'task_manager/mark_form.html', context)


def deleteMark(request, pk):
    mark = get_object_or_404(Mark, pk=pk)
    if request.method == 'POST':
        mark.delete()
        cache.delete('mark_list')  # Удаляем кэш после удаления
        return redirect('mark-list')

    context = {'object': mark}
    return render(request, 'task_manager/mark_confirm_delete.html', context)


# Задачи
def task_list(request):
    # Попробуем получить задачи из кэша
    cache_key = 'tasktype_list'
    tasks = cache.get(cache_key)

    if not tasks:
        tasks = TaskType.objects.all()
        cache.set(cache_key, tasks, timeout=60 * 15)  # Кэшируем на 15 минут

    form = TaskTypeForm()

    return render(request, 'task_manager/task_list.html', {'tasks': tasks, 'form': form})


def create_task(request):
    form = TaskTypeForm()

    if request.method == 'POST':
        form = TaskTypeForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            cache.delete('tasktype_list')  # Удаляем кэш после создания
            return redirect('task-list')

    return render(request, 'task_manager/task_form.html', {'form': form})


def update_task(request, pk):
    task = get_object_or_404(TaskType, pk=pk)
    form = TaskTypeForm(instance=task)

    if request.method == 'POST':
        form = TaskTypeForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            cache.delete('tasktype_list')  # Удаляем кэш после обновления
            return redirect('task-list')

    return render(request, 'task_manager/task_form.html', {'form': form, 'task': task})


def delete_task(request, pk):
    task = get_object_or_404(TaskType, pk=pk)

    if request.method == 'POST':
        task.delete()
        cache.delete('tasktype_list')  # Удаляем кэш после удаления
        return redirect('task-list')

    return render(request, 'task_manager/task_confirm_delete.html', {'task': task})


def parse_custom_date(date_str):
    # Убираем день недели и удаляем символ "г." в конце, если он есть
    date_str = date_str.split(",")[-1].strip()
    date_str = date_str.replace(" г.", "").strip()

    # Попробуем сначала стандартный формат "YYYY-MM-DD"
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    # Попробуем формат с русскими названиями месяцев
    months = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
        "мая": "05", "июня": "06", "июля": "07", "августа": "08",
        "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
    }

    # Обработка формата "дд ммм гггг"
    match = re.match(r"(\d{1,2}) (\w+) (\d{4})", date_str)
    if match:
        day, month_str, year = match.groups()
        month = months.get(month_str.lower())
        if month:
            return datetime.strptime(f"{year}-{month}-{day.zfill(2)}", "%Y-%m-%d").date()

    # Обработка формата "дд.мм.гггг"
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        pass

    # Если не удалось распознать формат
    raise ValueError(f"Unexpected date format: {date_str}")


# TimeLog
def timelog_list(request):
    # Получаем начальную и конечную даты из GET параметров
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())

    # Преобразуем даты с использованием parse_custom_date, если они строковые
    start_date = parse_custom_date(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_custom_date(end_date) if isinstance(end_date, str) else end_date

    # Кэшируем данные таймлогов, если кэш пуст
    timelogs = cache.get('timelogs_cache')
    if not timelogs:
        timelogs = (
            Timelog.objects.all()
            .select_related('user', 'role', 'department', 'project', 'building', 'mark', 'task')
            .prefetch_related('section')
        )
        # Сохраняем в кэше на 5 минут (300 секунд)
        cache.set('timelogs_cache', timelogs, timeout=900)

    # Применяем фильтры по параметрам
    if request.GET.get('user'):
        timelogs = timelogs.filter(user__id=request.GET.get('user'))
    if request.GET.get('project'):
        timelogs = timelogs.filter(project__id=request.GET.get('project'))
    if request.GET.get('stage'):
        timelogs = timelogs.filter(stage=request.GET.get('stage'))
    if request.GET.get('mark'):
        timelogs = timelogs.filter(mark__id=request.GET.get('mark'))

    # Фильтрация по диапазону дат
    if start_date and end_date:
        timelogs = timelogs.filter(date__range=[start_date, end_date])

    form = TimelogForm()

    context = {
        'timelogs': timelogs,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'task_manager/timelog_list.html', context)


@login_required
def timelog_create(request):
    if request.method == 'POST':
        form = TimelogForm(request.POST)
        if form.is_valid():
            # Получаем текущего пользователя
            user = request.user
            role = user.role  # Предполагается, что у пользователя есть роль

            # Создаем новый таймлог с указанием пользователя и его роли
            timelog = form.save(commit=False)
            timelog.user = user
            timelog.role = role
            timelog.save()
            cache.delete('timelogs_cache')

            return JsonResponse({'message': 'Таймлог успешно создан'}, status=200)

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


def timelog_update(request, pk):
    timelog = get_object_or_404(Timelog, pk=pk)
    form = TimelogForm(instance=timelog)

    if request.method == 'POST':
        form = TimelogForm(request.POST, instance=timelog)
        if form.is_valid():
            form.save()
            cache.delete('timelogs_cache')
            return redirect('timelog-list')

    context = {'form': form}
    return render(request, 'task_manager/timelog_form.html', context)


def timelog_delete(request, pk):
    timelog = get_object_or_404(Timelog, pk=pk)
    if request.method == 'POST':
        timelog.delete()
        return redirect('timelog-list')

    context = {'object': timelog}
    return render(request, 'task_manager/timelog_confirm_delete.html', context)


def reset_session(request):
    request.session.flush()  # Полностью очистит текущую сессию
    return redirect('login')


@login_required
def user_dashboard(request):
    user = request.user
    today = timezone.now().date()

    # Получаем таймлог за текущий день для данного пользователя
    timelog = Timelog.objects.filter(user=user, date__date=today).first()

    if request.method == 'POST' and not timelog:
        form = TimelogForm(request.POST)
        if form.is_valid():
            new_timelog = form.save(commit=False)
            new_timelog.user = user
            new_timelog.role = user.role  # Предполагаем, что у пользователя есть роль
            new_timelog.date = timezone.now()  # Устанавливаем дату на текущую
            new_timelog.save()
            return redirect('user-dashboard')
    else:
        form = TimelogForm()

    context = {
        'user': user,
        'timelog': timelog,
        'form': form,
        'today': today,
    }
    return render(request, 'task_manager/user_dashboard.html', context)


@login_required
def report_create(request):
    today = timezone.now().date()

    if request.method == 'POST':
        timelogs_data = []
        projects = request.POST.getlist('project')
        stages = request.POST.getlist('stage')
        sections = request.POST.getlist('section')
        buildings = request.POST.getlist('building')
        marks = request.POST.getlist('mark')
        tasks = request.POST.getlist('task')
        times = request.POST.getlist('time')

        for i in range(len(projects)):
            timelog = Timelog(
                user=request.user,
                role=request.user.role,
                department=request.user.department,
                project_id=projects[i],
                stage=stages[i],
                section_id=sections[i],
                building_id=buildings[i],
                mark_id=marks[i],
                task_id=tasks[i],
                time=int(times[i]),
                date=today
            )
            timelogs_data.append(timelog)

        # Сохраняем все таймлоги одним запросом
        Timelog.objects.bulk_create(timelogs_data)

        # Очищаем кэш, чтобы подтянуть актуальные данные при следующем запросе
        cache.delete('projects')
        cache.delete('sections')
        cache.delete('buildings')
        cache.delete('marks')
        cache.delete('tasks')
        cache.delete('timelogs_cache')

        return redirect('user-dashboard')  # Перенаправляем на список таймлогов

    else:
        form = TimelogForm()

    # Загружаем данные из кэша или базы данных для селектов
    projects = cache.get_or_set('projects', Project.objects.select_related('status').all(), timeout=60 * 15)
    sections = cache.get_or_set('sections', Section.objects.all(), timeout=60 * 15)
    buildings = cache.get_or_set('buildings', Building.objects.all(), timeout=60 * 15)
    marks = cache.get_or_set('marks', Mark.objects.all(), timeout=60 * 15)
    tasks = cache.get_or_set('tasks', TaskType.objects.all(), timeout=60 * 15)

    context = {
        'form': form,
        'today': today,
        'projects': projects,
        'stages': Timelog._meta.get_field('stage').choices,
        'sections': sections,
        'buildings': buildings,
        'marks': marks,
        'tasks': tasks,
    }

    return render(request, 'task_manager/report_create.html', context)


def reports_view(request):
    # Получаем начальную и конечную даты из GET параметров
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())

    # Преобразуем даты с использованием новой функции
    start_date = parse_custom_date(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_custom_date(end_date) if isinstance(end_date, str) else end_date

    # Фильтрация Timelog по диапазону дат
    timelogs = (
        Timelog.objects
        .filter(date__range=[start_date, end_date])
        .select_related('project', 'department', 'user', 'building', 'mark', 'task')
    )

    # Группировка данных по проектам
    detailed_report_projects = {}
    for item in timelogs:
        project_title = item.project.title
        if project_title not in detailed_report_projects:
            detailed_report_projects[project_title] = {
                'entries': [],
                'total_time': 0
            }
        detailed_report_projects[project_title]['entries'].append(item)
        detailed_report_projects[project_title]['total_time'] += item.time

    # Общий итог времени по всем проектам
    overall_total_time_projects = sum([group['total_time'] for group in detailed_report_projects.values()])

    # Группировка данных по отделам
    detailed_report_departments = {}
    for item in timelogs:
        department_title = item.department.title
        if department_title not in detailed_report_departments:
            detailed_report_departments[department_title] = {
                'entries': [],
                'total_time': 0
            }
        detailed_report_departments[department_title]['entries'].append(item)
        detailed_report_departments[department_title]['total_time'] += item.time

    # Общий итог времени по всем отделам
    overall_total_time_departments = sum([group['total_time'] for group in detailed_report_departments.values()])

    context = {
        'detailed_report_projects': detailed_report_projects,
        'overall_total_time_projects': overall_total_time_projects,
        'detailed_report_departments': detailed_report_departments,
        'overall_total_time_departments': overall_total_time_departments,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'task_manager/reports.html', context)


def reports_employees(request):
    # Получаем начальную и конечную даты из GET параметров
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())

    # Преобразуем даты с использованием новой функции
    start_date = parse_custom_date(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_custom_date(end_date) if isinstance(end_date, str) else end_date

    # Получаем все записи Timelog с оптимизацией связанных данных
    timelogs = (
        Timelog.objects
        .select_related('project', 'department', 'user', 'building', 'mark', 'task')
        .all()
    )

    # Группировка данных по проектам
    detailed_report_projects = {}
    for item in timelogs:
        project_title = item.project.title
        if project_title not in detailed_report_projects:
            detailed_report_projects[project_title] = {
                'entries': [],
                'total_time': 0
            }
        detailed_report_projects[project_title]['entries'].append(item)
        detailed_report_projects[project_title]['total_time'] += item.time

    # Общий итог времени по всем проектам
    overall_total_time_projects = sum([group['total_time'] for group in detailed_report_projects.values()])

    # Группировка данных по отделам
    detailed_report_departments = {}
    for item in timelogs:
        department_title = item.department.title
        if department_title not in detailed_report_departments:
            detailed_report_departments[department_title] = {
                'entries': [],
                'total_time': 0
            }
        detailed_report_departments[department_title]['entries'].append(item)
        detailed_report_departments[department_title]['total_time'] += item.time

    # Общий итог времени по всем отделам
    overall_total_time_departments = sum([group['total_time'] for group in detailed_report_departments.values()])

    context = {
        'detailed_report_projects': detailed_report_projects,
        'overall_total_time_projects': overall_total_time_projects,
        'detailed_report_departments': detailed_report_departments,
        'overall_total_time_departments': overall_total_time_departments,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'task_manager/reports_employees.html', context)


def get_months_in_range(start_date, end_date):
    """Получение всех месяцев до последнего месяца в диапазоне"""
    months = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date.replace(day=1):
        months.append(current_date)
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    return months[:-1]  # Все месяцы, кроме последнего


def get_days_in_month(month_date):
    """Получение всех дней для последнего месяца"""
    next_month = month_date.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    return [month_date + timedelta(days=i) for i in range((end_of_month - month_date).days + 1)]


def final_report(request):
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())

    # Преобразуем даты с использованием новой функции
    start_date = parse_custom_date(start_date) if isinstance(start_date, str) else start_date
    end_date = parse_custom_date(end_date) if isinstance(end_date, str) else end_date

    timelogs = Timelog.objects.filter(date__range=[start_date, end_date])

    report_data = timelogs.values('project__title', 'building__title', 'mark__title').annotate(
        total_hours=Sum('time'),
        user_full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name'))
    )

    # Получаем месяцы до последнего и дни последнего месяца
    months_in_range = get_months_in_range(start_date, end_date)
    days_in_last_month = get_days_in_month(end_date.replace(day=1))

    # Группировка данных по месяцам и дням
    monthly_hours = {}
    grouped_hours = {}
    last_month_key = end_date.strftime('%Y-%m')

    for log in timelogs:
        key_str = f"{log.project.title}|{log.building.title}|{log.mark.title}|{log.user.first_name} {log.user.last_name}"
        month_key = log.date.strftime('%Y-%m')
        day_key = log.date.strftime('%Y-%m-%d')

        if month_key != last_month_key:
            # Группируем по месяцам, кроме последнего
            if key_str not in grouped_hours:
                grouped_hours[key_str] = {}
            grouped_hours[key_str][month_key] = grouped_hours[key_str].get(month_key, 0) + log.time
        else:
            # Последний месяц по дням
            if key_str not in monthly_hours:
                monthly_hours[key_str] = {}
            monthly_hours[key_str][day_key] = log.time

    context = {
        'report_data': report_data,
        'months_in_range': months_in_range,
        'days_in_last_month': days_in_last_month,
        'grouped_hours': grouped_hours,
        'monthly_hours': monthly_hours,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'task_manager/final_report.html', context)


def parse_russian_date(date_str):
    # Словарь для замены русских названий месяцев на числовые значения
    month_translation = {
        'января': '01', 'февраля': '02', 'марта': '03',
        'апреля': '04', 'мая': '05', 'июня': '06',
        'июля': '07', 'августа': '08', 'сентября': '09',
        'октября': '10', 'ноября': '11', 'декабря': '12'
    }

    # Убираем символ "г." в конце строки
    date_str = re.sub(r'\sг\.$', '', date_str)

    # Заменяем русские названия месяцев на числовые значения
    for ru_month, num_month in month_translation.items():
        date_str = date_str.replace(ru_month, num_month)

    # Преобразуем строку в формат YYYY-MM-DD
    try:
        return datetime.strptime(date_str, '%d %m %Y').date()
    except ValueError as e:
        print(f"Ошибка преобразования даты: {e}")
        return None


def export_to_excel(request):
    # Получаем строки дат из запроса
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    print("Received start_date_str:", start_date_str)
    print("Received end_date_str:", end_date_str)

    # Парсим даты с использованием dateparser
    start_date = dateparser.parse(start_date_str).date() if start_date_str else timezone.now().replace(day=1).date()
    end_date = dateparser.parse(end_date_str).date() if end_date_str else timezone.now().date()

    # Проверка на наличие start_date и end_date после парсинга
    if start_date is None or end_date is None:
        print("Error: start_date or end_date is None")
        return HttpResponse("Ошибка: некорректные даты", status=400)

    print("Parsed start_date:", start_date)
    print("Parsed end_date:", end_date)

    # Получаем данные из базы данных
    timelogs = Timelog.objects.filter(date__range=[start_date, end_date])

    # Создаем переменные для хранения часов по месяцам и дням
    grouped_hours = {}
    monthly_hours = {}

    last_month_key = end_date.strftime('%Y-%m')
    for log in timelogs:
        key_str = f"{log.project.title}|{log.building.title}|{log.mark.title}|{log.user.first_name} {log.user.last_name}"
        month_key = log.date.strftime('%Y-%m')

        if month_key != last_month_key:
            # Группируем по месяцам, кроме последнего
            if key_str not in grouped_hours:
                grouped_hours[key_str] = {}
            grouped_hours[key_str][month_key] = grouped_hours[key_str].get(month_key, 0) + log.time
        else:
            # Последний месяц по дням
            if key_str not in monthly_hours:
                monthly_hours[key_str] = {}
            daily_key = log.date.strftime('%Y-%m-%d')
            monthly_hours[key_str][daily_key] = log.time

    # Создаем новую книгу Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчет по таймлогам"

    # Записываем заголовки
    headers = ["Объект", "ЗиС", "Марка", "Исполнитель", "Часы"]
    months_in_range = get_months_in_range(start_date, end_date)
    days_in_last_month = get_days_in_month(end_date.replace(day=1))

    for month in months_in_range:
        headers.append(month.strftime("%B %Y"))  # Заголовок месяца
    for day in days_in_last_month:
        headers.append(day.strftime("%d %b %Y"))  # Заголовок дня

    ws.append(headers)

    # Стилизация для заливки ячеек с данными
    fill_style = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")

    # Обработка данных для экспорта
    for item in timelogs.values('project__title', 'building__title', 'mark__title').annotate(
            total_hours=Sum('time'),
            user_full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name'))
    ):
        row = [
            item['project__title'],
            item['building__title'],
            item['mark__title'],
            item['user_full_name'],
            f"{item['total_hours']} ч"
        ]

        # Добавляем данные по месяцам
        for month in months_in_range:
            month_key = month.strftime("%Y-%m")
            hours = grouped_hours.get(
                f"{item['project__title']}|{item['building__title']}|{item['mark__title']}|{item['user_full_name']}",
                {}).get(month_key, "-")
            row.append(hours)
            if hours != "-":
                ws[f"{get_column_letter(len(row))}{ws.max_row}"].fill = fill_style  # Заливаем ячейку

        # Добавляем данные по дням последнего месяца
        for date in days_in_last_month:
            day_key = date.strftime("%Y-%m-%d")
            hours = monthly_hours.get(
                f"{item['project__title']}|{item['building__title']}|{item['mark__title']}|{item['user_full_name']}",
                {}).get(day_key, "-")
            row.append("*" if hours != "-" else hours)

        ws.append(row)

    # Настройка ширины колонок и выравнивание
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 15
        for cell in ws[get_column_letter(col)]:
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Генерация ответа с файлом Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="timelog_report.xlsx"'
    wb.save(response)
    return response
