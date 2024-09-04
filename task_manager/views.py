from django.core import paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth.models import UserManager
from .models import Department, ProjectStatus, Role, CustomUser, Project, ProjectBuilding, ProjectSection, Building, Section
from .forms import DepartmentForm, RoleForm, CustomUserCreationForm, CustomUserChangeForm, ProjectForm, ProjectBuildingForm, ProjectSectionForm
from django.db.models import Q


def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_authenticated and u.is_admin, login_url=login_url)

# Отделы
@admin_required(login_url='login')
def department(request):
    departmentObj = Department.objects.all()
    form = DepartmentForm()

    return render(request, 'task_manager/departments_list.html', {'departments': departmentObj, 'form': form})


def createDepartment(request):
    form = DepartmentForm()

    if request.method == 'POST':

        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            
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

            return redirect('department-list')

    context = {'form': form, 'department': department}
    return render(request, 'task_manager/department_form.html', context)


def deleteDepartment(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':

        department.delete()

        return redirect('department-list')
    
    context = {'object': department}
    return render(request, 'task_manager/department_form.html', context)


# Должности
@admin_required(login_url='login')
def role(request):
    roleObj = Role.objects.all()
    form = RoleForm()

    return render(request, 'task_manager/roles_list.html', {'roles': roleObj, 'form': form})


def createRole(request):
    form = RoleForm()

    if request.method == 'POST':

        form = RoleForm(request.POST, request.FILES)
        if form.is_valid():
            role = form.save(commit=False)
            role.save()
            
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

            return redirect('role-list')

    context = {'form': form, 'role': role}
    return render(request, 'task_manager/role_form.html', context)


def deleteRole(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':

        role.delete()

        return redirect('role-list')
    
    context = {'object': role}
    return render(request, 'task_manager/role_form.html', context)


# Юзеры
@admin_required(login_url='login')
def user(request):
    users = CustomUser.objects.all()
    departments = Department.objects.all()
    roles = Role.objects.all()

    # Apply filters if any
    status = request.GET.get('status')
    department = request.GET.get('department')
    role = request.GET.get('role')
    last_name = request.GET.get('last_name')

    if status:
        users = users.filter(status=status)
    if department:
        users = users.filter(department__id=department)
    if role:
        users = users.filter(role__id=role)
    if last_name:
        users = users.filter(last_name__icontains=last_name)

    form = CustomUserCreationForm()
    return render(request, 'task_manager/users_list.html', {'users': users, 'form': form, 'departments': departments, 'roles': roles})


def createUser(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
            return redirect('user-list')
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {'form': form, 'user': user}
    return render(request, 'task_manager/user_form.html', context)


def deleteUser(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
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

        # Отправка письма-приглашения с логином и паролем
        send_mail(
            'Приглашение на платформу Task Manager',
            f'Ваши учетные данные для входа:\nЛогин: {user.username}\nПароль: {password}',
            'noreply@taskmanager.com',
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
    project_buildings = ProjectBuilding.objects.filter(project=project)
    project_sections = ProjectSection.objects.filter(project=project)
    return render(request, 'task_manager/project_detail.html', {
        'project': project, 
        'project_buildings': project_buildings,
        'project_sections': project_sections
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
            return redirect('project-detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'task_manager/project_form.html', {'form': form})

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
