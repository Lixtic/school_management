from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0010_resource_link_resource_target_audience_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="curriculum",
            field=models.CharField(
                choices=[
                    ("ges_jhs_new", "GES New Curriculum (JHS)"),
                    ("ges_basic", "GES Basic School"),
                    ("waec_legacy", "WAEC/Legacy"),
                    ("cambridge_lower", "Cambridge Lower Secondary"),
                    ("other", "Other/General"),
                ],
                default="ges_jhs_new",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="resource",
            name="resource_type",
            field=models.CharField(
                choices=[("curriculum", "Curriculum"), ("teaching", "Teaching Resource")],
                default="teaching",
                max_length=20,
            ),
        ),
    ]
