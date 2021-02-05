from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0001_squashed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='content_md',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='section',
            name='content_ck',
        ),
        migrations.RemoveField(
            model_name='section',
            name='validated',
        ),
        migrations.AddField(
            model_name='answer',
            name='validation_status',
            field=models.IntegerField(
                choices=[
                    (0, 'Não verificado'), (1, 'Rascunho'), (2, 'Incorrecto'), (3, 'Correcto')],
                default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='answer',
            name='validator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='validated_questions',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer',
            name='validator_note',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='related',
            field=models.ManyToManyField(
                blank=True,
                related_name='related_to',
                to='learning.Section',
                verbose_name='relacionados'),
        ),
        migrations.AddField(
            model_name='section',
            name='validation_status',
            field=models.IntegerField(
                choices=[(0, 'Não verificado'), (1, 'Rascunho'), (2, 'Incorrecto'), (3, 'Correcto')],
                default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='validator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='validated_sections',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='validator_note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
