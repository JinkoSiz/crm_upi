import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0004_remove_customuser_position_customuser_is_admin'),
    ]

    operations = [
        # Step 2: Remove the old `id` field
        migrations.RemoveField(
            model_name='customuser',
            name='id',
        ),
        # Step 3: Rename `new_uuid` to `id` and make it the primary key
        migrations.RenameField(
            model_name='customuser',
            old_name='new_uuid',
            new_name='id',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
    ]
