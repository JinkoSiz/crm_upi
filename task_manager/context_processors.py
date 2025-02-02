from task_manager.models import *

def all_users(request):
    """
    Контекстный процессор для добавления всех данных в контекст, с фильтрацией зданий по проектам.
    """
    all_users = CustomUser.objects.all()
    all_roles = Role.objects.all()
    all_departments = Department.objects.all()
    all_projects = Project.objects.all()  # Все проекты
    all_sections = Section.objects.all()
    all_marks = Mark.objects.all()
    all_tasks = TaskType.objects.all()

    # Фильтрация зданий по выбранным проектамBc
    all_buildings = Building.objects.all()
    selected_projects = request.GET.get('project', '')  # Получаем строку проектов из GET

    if selected_projects:
        # Разделяем строку на названия проектов
        project_titles = [title.strip() for title in selected_projects.split(',')]

        # Фильтруем проекты по их названиям
        project_ids = Project.objects.filter(title__in=project_titles).values_list('id', flat=True)

        # Фильтруем здания через ProjectBuilding
        all_buildings = Building.objects.filter(
            id__in=ProjectBuilding.objects.filter(project__id__in=project_ids).values_list('building_id', flat=True)
        )

    return {
        'all_users': all_users,
        'all_roles': all_roles,
        'all_departments': all_departments,
        'all_projects': all_projects,  # Все проекты
        'all_sections': all_sections,
        'all_buildings': all_buildings,  # Фильтрованные здания
        'all_marks': all_marks,
        'all_tasks': all_tasks,
    }
