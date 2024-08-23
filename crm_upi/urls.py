from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('task_manager.urls')),  # Подключаем URLs из task_manager
]
