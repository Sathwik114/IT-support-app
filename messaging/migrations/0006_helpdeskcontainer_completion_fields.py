from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_helpdeskcontainer_fixed_problem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='helpdeskcontainer',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='helpdeskcontainer',
            name='completed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='completed_containers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='helpdeskcontainer',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('took_over', 'Took Over'),
                    ('completed', 'Completed'),
                    ('resolved', 'Resolved'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
