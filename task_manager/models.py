import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class ProjectStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True, default='Default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Building(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)  # Убираем unique=True
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Mark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    status = models.ForeignKey(ProjectStatus, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    is_admin = models.BooleanField(default=False, help_text='Designates whether the user is an administrator.')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='users')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='users')
    status = models.CharField(max_length=255, choices=[
        ('draft', 'Черновик'),
        ('invited', 'Приглашен'),
        ('active', 'Активен'),
        ('fired', 'Уволен')
    ])
    email = models.EmailField(unique=True)
    foto = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # уникальное имя обратного отношения
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # уникальное имя обратного отношения
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        # Save the user first to ensure it has an ID
        super().save(*args, **kwargs)
        # Custom logic when is_admin is set
        if self.is_admin or self.is_superuser:
            admin_group, created = Group.objects.get_or_create(name='Admin')
            self.groups.add(admin_group)

            # Ensure all permissions are granted to the admin
            permissions = Permission.objects.all()
            self.user_permissions.set(permissions)
            self.is_staff = True
            self.is_superuser = True
            if self.status != 'invited' and self.status != 'active':
                self.status = 'draft'
        else:
            # Clear admin rights if is_admin is False
            self.is_staff = False
            self.is_superuser = False
            print(f'models {self.status}')
            if self.status != 'invited' and self.status != 'active':
                #print(f'models {self.status}')
                self.status = 'draft'
            admin_group = Group.objects.filter(name='Admin').first()
            if admin_group:
                self.groups.remove(admin_group)
            self.user_permissions.clear()

        # Save again to persist the changes made after the initial save
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]


class ProjectBuilding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_buildings')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='project_buildings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'building')


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProjectSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_sections')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='project_sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'section')


class SectionMark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_marks')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, related_name='section_marks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('section', 'mark')


class Timelog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='timelogs')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='timelogs')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='timelogs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timelogs')
    stage = models.CharField(max_length=255, choices=[
        ('PD', 'ПД'),
        ('RD', 'РД'),
        ('OTR', 'ОТР')
    ])
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timelogs', null=True, blank=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='timelogs')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, related_name='timelogs')
    task = models.ForeignKey(TaskType, on_delete=models.CASCADE, related_name='timelogs')
    date = models.DateTimeField()
    time = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.project} - {self.date}'

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
            models.Index(fields=['project']),
            models.Index(fields=['section']),
            models.Index(fields=['building']),
            models.Index(fields=['mark']),
            models.Index(fields=['task']),
        ]

