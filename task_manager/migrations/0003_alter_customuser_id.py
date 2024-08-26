import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0002_customuser_middle_name'),
    ]

    operations = [
        # Step 1: Add a new UUID field
        migrations.AddField(
            model_name='customuser',
            name='new_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
