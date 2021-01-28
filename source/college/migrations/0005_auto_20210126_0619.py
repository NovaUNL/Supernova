from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('college', '0004_auto_20210118_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='improvement_grade',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='improvement_grade_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
