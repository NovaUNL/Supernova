from django.conf import settings
from django.db import migrations, models
from django.db import migrations
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):
    replaces = [('feedback', '0001_initial'), ('feedback', '0002_auto_20201010_2107'),
                ('feedback', '0003_auto_20201011_0553'), ('feedback', '0004_auto_20201014_1143'),
                ('feedback', '0005_remove_vote_to'), ('feedback', '0006_auto_20201111_0604'),
                ('feedback', '0007_suggestion'), ('feedback', '0008_auto_20201112_0434'),
                ('feedback', '0009_auto_20201227_2031')]

    initial = True

    dependencies = [
        ('feedback', '0001_squashed'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.activity')),
                ('anonymity', models.BooleanField(default=True)),
                ('object_id', models.PositiveIntegerField()),
                ('type', models.IntegerField(choices=[(0, 'positivo'), (1, 'negativo'), (2, 'favorito')])),
                ('content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.activity',),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.activity')),
                ('upvotes', models.IntegerField(default=0)),
                ('downvotes', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=300)),
                ('content', markdownx.models.MarkdownxField(max_length=2000)),
                ('towards_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('status',
                 models.IntegerField(
                     choices=[(0, 'proposta'), (1, 'em progresso'), (2, 'concluida'), (3, 'rejeitada')],
                     default=0)),
                ('towards_content_type',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
            },
            bases=('users.activity', models.Model),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.activity')),
                ('object_id', models.PositiveIntegerField()),
                ('text', models.TextField(blank=True, null=True)),
                ('rating', models.IntegerField()),
                ('anonymity', models.BooleanField(default=False)),
                ('content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.activity',),
        ),
        migrations.AddField(
            model_name='report',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='report',
            name='reporter',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reports',
                to=settings.AUTH_USER_MODEL),
        ),
    ]
