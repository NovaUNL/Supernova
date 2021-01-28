import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('college', '0003_curricular_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='links',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.URLField(),
                blank=True,
                null=True,
                size=None),
        ),
        migrations.AddField(
            model_name='file',
            name='meta',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='pages',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                blank=True,
                null=True,
                size=None),
        ),
        migrations.AddField(
            model_name='file',
            name='process_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='classfile',
            name='name',
            field=models.CharField(default='-', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='curricularblockvariantcomponent',
            name='blocked_components',
            field=models.ManyToManyField(
                blank=True,
                related_name='curricular_blocks',
                to='college.CurricularComponent'),
        ),
    ]
