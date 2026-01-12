from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teachers", "0003_lessonplan"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="notification_ahead_minutes",
            field=models.PositiveIntegerField(default=45, help_text="Minutes before lesson to be notified"),
        ),
    ]
