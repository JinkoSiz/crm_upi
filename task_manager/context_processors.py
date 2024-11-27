from task_manager.models import *


def all_users(request):
    """
    Контекстный процессор для добавления всех пользователей в контекст.
    """
    all_users = CustomUser.objects.all()  # Получаем всех пользователей
    all_roles = Role.objects.all()
    all_departments = Department.objects.all()
    all_projects = Project.objects.all()
    all_sections = Section.objects.all()
    all_buildings = Building.objects.all()
    all_marks = Mark.objects.all()
    all_tasks = TaskType.objects.all()
    return {'all_users': all_users,
            'all_roles': all_roles,
            'all_departments': all_departments,
            'all_projects': all_projects,
            'all_sections': all_sections,
            'all_buildings': all_buildings,
            'all_marks': all_marks,
            'all_tasks': all_tasks,
            }
