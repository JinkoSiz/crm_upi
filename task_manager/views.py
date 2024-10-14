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
from .models import Department, ProjectStatus, Role, CustomUser, Project, ProjectBuilding, ProjectSection, Building, \
    Section, Mark, SectionMark
from .forms import DepartmentForm, RoleForm, CustomUserCreationForm, CustomUserChangeForm, ProjectForm, \
    ProjectBuildingForm, ProjectSectionForm, SectionForm, MarkForm
from django.db.models import Q
from django.views.decorators.cache import cache_page



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
            return redirect('department-list')  # Redirect to your desired page after login
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'task_manager/login.html')


def user_logout(request):
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
    projects = Project.objects.all()
    project_statuses = ProjectStatus.objects.all()
    form = ProjectForm()
    return render(request, 'task_manager/project_list.html', {
        'projects': projects,
        'project_statuses': project_statuses,
        'form': form
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Получаем связанные здания и секции
    project_buildings = ProjectBuilding.objects.filter(project=project)
    project_sections = ProjectSection.objects.filter(project=project)

    # Получаем все доступные здания и секции для отображения в форме
    buildings = Building.objects.all()
    sections = Section.objects.all()

    # Получаем список всех PK секций для данного проекта
    project_section_pks = project_sections.values_list('section__pk', flat=True)
    project_building_pks = project_buildings.values_list('building__pk', flat=True)

    return render(request, 'task_manager/project_detail.html', {
        'project': project,
        'project_buildings': project_buildings,  # Передаем объекты ProjectBuilding для отображения
        'project_sections': project_sections,  # Передаем объекты ProjectSection для отображения
        'buildings': buildings,  # Все здания для отображения в форме
        'sections': sections,  # Все секции для отображения в форме
        'project_building_pks': project_building_pks,  # Список PK зданий для этого проекта
        'project_section_pks': project_section_pks,  # Список PK секций для этого проекта
        'project_status': ProjectStatus.objects.all(),  # Статусы проектов для выбора
    })


def createProject(request):
    form = ProjectForm()

    if request.method == 'POST':

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            role = form.save(commit=False)
            role.save()

            return redirect('project-list')

    context = {'form': form}
    return render(request, 'task_manager/project_form.html', context)


def updateProject(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            # Обработка зданий
            buildings = request.POST.getlist('buildings')  # Получаем список зданий из формы
            ProjectBuilding.objects.filter(project=project).delete()  # Удаляем старые здания
            for building_id in buildings:
                building = Building.objects.get(pk=building_id)
                ProjectBuilding.objects.create(project=project, building=building)

            # Обработка секций (аналогично для секций)
            sections = request.POST.getlist('sections')
            ProjectSection.objects.filter(project=project).delete()
            for section_id in sections:
                section = Section.objects.get(pk=section_id)
                ProjectSection.objects.create(project=project, section=section)

            return redirect('project-detail', pk=pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'task_manager/project_form.html', {'form': form, 'project': project})


def deleteProject(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project-list')
    return render(request, 'task_manager/project_confirm_delete.html', {'project': project})


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