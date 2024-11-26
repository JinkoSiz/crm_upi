from task_manager.models import CustomUser


def all_users(request):
    """
    Контекстный процессор для добавления всех пользователей в контекст.
    """
    all_users = CustomUser.objects.all()  # Получаем всех пользователей
    return {'all_users': all_users}
