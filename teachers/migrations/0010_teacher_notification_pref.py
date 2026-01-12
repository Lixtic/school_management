from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teachers", "0009_merge_20241028_1657"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="notification_ahead_minutes",
            field=models.PositiveIntegerField(default=45, help_text="Minutes before lesson to be notified"),
        ),
    ]
