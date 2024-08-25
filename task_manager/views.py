from django.core import paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth.models import UserManager
from .models import Department, Role, CustomUser
from .forms import DepartmentForm, RoleForm, CustomUserCreationForm, CustomUserChangeForm

# Отделы

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

def user(request):
    users = CustomUser.objects.all()
    form = CustomUserCreationForm()
    return render(request, 'task_manager/users_list.html', {'users': users, 'form': form})


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
