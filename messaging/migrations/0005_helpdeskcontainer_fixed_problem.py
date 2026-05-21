from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_helpdeskcontainer_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpdeskcontainer',
            name='fixed_problem',
            field=models.TextField(blank=True),
        ),
    ]
