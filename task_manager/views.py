from django.core import paginator
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth.models import UserManager
from .models import *
from .forms import *
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils import timezone



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
    cache_key = 'user_list'
    users = cache.get(cache_key)

    # Применяем кэш только если нет фильтров
    if not users and not (request.GET.get('status') or request.GET.get('department') or request.GET.get('role') or request.GET.get('last_name')):
        users = CustomUser.objects.select_related('department', 'role').all()
        cache.set(cache_key, users, timeout=60 * 5)  # Кэшируем на 5 минут

    # Применяем фильтры
    if request.GET.get('status'):
        users = users.filter(status=request.GET.get('status'))
    if request.GET.get('department'):
        users = users.filter(department__id=request.GET.get('department'))
    if request.GET.get('role'):
        users = users.filter(role__id=request.GET.get('role'))
    if request.GET.get('last_name'):
        users = users.filter(last_name__icontains=request.GET.get('last_name'))

    departments = Department.objects.all()
    roles = Role.objects.all()
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
            cache.delete('user_list')  # Очищаем кэш

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

        return redirect('user-list')

    return render(request, 'task_manager/user_confirm_delete.html', {'user': user})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
    user = get_object_or_404(CustomUser, pk=pk)
    if user.status != 'invited':
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

        # Синхронная отправка email
        send_mail(
            'Приглашение на платформу Task Manager',
            f'Ваши учетные данные для входа:\nЛогин: {user.username}\nПароль: {password}',
            'zpsk1977@gmail.com',
            [user.email],
            fail_silently=False,
        )

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
    # Используем select_related для выборки связанных данных статус проекта
    projects = Project.objects.all().select_related('status').prefetch_related('project_buildings__building', 'project_sections__section')
    
    project_status = ProjectStatus.objects.all()
    sections = Section.objects.all()  # Получаем все разделы
    form = ProjectForm()
    
    return render(request, 'task_manager/project_list.html', {
        'projects': projects,
        'project_status': project_status,
        'sections': sections,  # Передаем разделы в шаблон
        'form': form
    })

def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('project_buildings__building', 'project_sections__section'), pk=pk)

    buildings = project.project_buildings.values('building__pk', 'building__title')
    sections = project.project_sections.values('section__pk', 'section__title')

    return JsonResponse({
        'project': {
            'title': project.title,
            'status': project.status_id
        },
        'buildings': list(buildings),
        'sections': list(sections)  # Добавляем секции для отображения
    })

def createProject(request):
    if request.method == 'POST':
        title = request.POST['title']
        status_id = request.POST['status']
        sections = request.POST.getlist('sections')

        project = Project.objects.create(title=title, status_id=status_id)

        # Обработка зданий
        buildings = request.POST.getlist('buildings[]')  # Получаем список зданий из формы
        ProjectBuilding.objects.filter(project=project).delete()  # Удаляем старые здания
        print(buildings)
        for building_title in buildings:
            # Проверяем, существует ли здание с таким названием, если нет - создаем
            building, created = Building.objects.get_or_create(title=building_title)
            ProjectBuilding.objects.create(project=project, building=building)
        
        # Добавляем выбранные разделы к проекту
        for section_id in sections:
            section = Section.objects.get(pk=section_id)
            ProjectSection.objects.create(project=project, section=section)

        return JsonResponse({'message': 'Проект создан'})

def updateProject(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        
        # Обновляем название и статус проекта
        project.title = request.POST['title']
        project.status_id = request.POST['status']
        project.save()

        # Обработка зданий
        buildings = request.POST.getlist('buildings[]')  # Получаем список зданий из формы
        ProjectBuilding.objects.filter(project=project).delete()  # Удаляем старые здания
        print(buildings)
        for building_title in buildings:
            # Проверяем, существует ли здание с таким названием, если нет - создаем
            building, created = Building.objects.get_or_create(title=building_title)
            ProjectBuilding.objects.create(project=project, building=building)

        # Обработка разделов
        sections = request.POST.getlist('sections[]')  # Получаем список разделов из формы
        print(sections)
        ProjectSection.objects.filter(project=project).delete()  # Удаляем старые разделы
        for section_id in sections:
            section = Section.objects.get(pk=section_id)
            ProjectSection.objects.create(project=project, section=section)
        
        return JsonResponse({'message': 'Проект обновлен'})


def deleteProject(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.delete()
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


# TimeLog
def timelog_list(request):
    # Оптимизация запросов с использованием select_related и prefetch_related
    timelogs = Timelog.objects.all().select_related('user', 'role', 'department', 'project', 'building', 'mark', 'task').prefetch_related('section')

    if request.GET.get('user'):
        timelogs = timelogs.filter(user__id=request.GET.get('user'))
    if request.GET.get('project'):
        timelogs = timelogs.filter(project__id=request.GET.get('project'))
    if request.GET.get('stage'):
        timelogs = timelogs.filter(stage=request.GET.get('stage'))
    if request.GET.get('mark'):
        timelogs = timelogs.filter(mark__id=request.GET.get('mark'))
    
    form = TimelogForm()

    context = {
        'timelogs': timelogs,
        'form': form
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

            return JsonResponse({'message': 'Таймлог успешно создан'}, status=200)

    return JsonResponse({'error': 'Неверный запрос'}, status=400)

def timelog_update(request, pk):
    timelog = get_object_or_404(Timelog, pk=pk)
    form = TimelogForm(instance=timelog)

    if request.method == 'POST':
        form = TimelogForm(request.POST, instance=timelog)
        if form.is_valid():
            form.save()
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
