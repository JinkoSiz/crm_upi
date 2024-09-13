from celery import shared_task
from django.core.mail import send_mail
from .models import CustomUser


@shared_task
def send_invitation_email_task(user_id):
    user = CustomUser.objects.get(pk=user_id)
    send_mail(
        'Приглашение на платформу Task Manager',
        f'Ваши учетные данные для входа:\nЛогин: {user.username}\nПароль: {user.password}',
        'zpsk1977@gmail.com',
        [user.email],
        fail_silently=False,
    )


@shared_task
def reset_password_task(user_id, new_password):
    user = CustomUser.objects.get(pk=user_id)
    user.set_password(new_password)
    user.save()

    send_mail(
        'Ваш новый пароль',
        f'Ваш новый пароль: {new_password}',
        'noreply@taskmanager.com',  # Email отправителя
        [user.email],
        fail_silently=False,
    )