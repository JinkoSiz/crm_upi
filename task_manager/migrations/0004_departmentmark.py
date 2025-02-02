# Generated by Django 5.1 on 2025-01-22 10:16

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0003_remove_customuser_first_login_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentMark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='department_marks', to='task_manager.department')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='department_marks', to='task_manager.mark')),
            ],
            options={
                'unique_together': {('department', 'mark')},
            },
        ),
    ]
