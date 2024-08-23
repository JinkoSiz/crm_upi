from django.core import paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Role
from .forms import DepartmentForm, RoleForm

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