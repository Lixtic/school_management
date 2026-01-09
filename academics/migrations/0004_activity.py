from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_alter_class_unique_together_remove_class_section'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('summary', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('tag', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_staff', models.ManyToManyField(blank=True, related_name='assigned_activities', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', '-created_at'],
            },
        ),
    ]
