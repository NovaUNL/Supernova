from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('documents', '0001_initial')]

    initial = True

    dependencies = [
        ('groups', '0001_squashed'),
        ('users', '0001_squashed'),
        ('documents', '0001_squashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='grouppermission',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.document'),
        ),
        migrations.AddField(
            model_name='grouppermission',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.group'),
        ),
        migrations.AddField(
            model_name='document',
            name='author_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='groups.group'),
        ),
        migrations.AddField(
            model_name='document',
            name='author_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='document_author',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='last_editor',
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='document_editor',
                to=settings.AUTH_USER_MODEL),
        ),
    ]
