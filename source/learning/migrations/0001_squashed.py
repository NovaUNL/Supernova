from django.conf import settings
from django.db import migrations, models
from django.db import migrations
import django.db.models.deletion
import learning.models
import markdownx.models


class Migration(migrations.Migration):
    replaces = [
        ('learning', '0001_initial'), ('learning', '0002_questions'), ('learning', '0003_auto_20200906_0413'),
        ('learning', '0004_auto_20201011_0059'), ('learning', '0005_auto_20201011_1109'),
        ('learning', '0006_questionanswer_teacher_accepted'), ('learning', '0007_auto_20201015_0559'),
        ('learning', '0008_auto_20201015_0605'), ('learning', '0009_auto_20201015_0616'),
        ('learning', '0010_auto_20201015_0624'), ('learning', '0011_auto_20201015_0909'),
        ('learning', '0012_auto_20201019_1012'), ('learning', '0013_answernotification'),
        ('learning', '0014_section_type'), ('learning', '0015_auto_20201227_2031')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0001_squashed'),
        ('college', '0001_squashed'),
        ('documents', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
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
                ('content', markdownx.models.MarkdownxField()),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('edit_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.activity', models.Model),
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('image', models.ImageField(blank=True, null=True, upload_to=learning.models.area_pic_path)),
                ('img_url', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='ClassSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('corresponding_class',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='synopsis_sections_rel',
                     to='college.class')),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(blank=True, max_length=256, null=True, verbose_name='origem')),
                ('source_url', models.URLField(blank=True, null=True, verbose_name='endereço')),
                ('successes', models.IntegerField(default=0)),
                ('failures', models.IntegerField(default=0)),
                ('skips', models.IntegerField(default=0)),
                ('author',
                 models.ForeignKey(
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='contributed_exercises',
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('content_md', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('content_ck', models.TextField(blank=True, null=True)),
                ('validated', models.BooleanField(default=False)),
                ('type',
                 models.IntegerField(
                     choices=[(0, 'Tópico'), (1, 'Personalidade'), (2, 'Aplicação')],
                     default=0,
                     verbose_name='tipo')),
                ('classes',
                 models.ManyToManyField(
                     blank=True,
                     related_name='synopsis_sections',
                     through='learning.ClassSection',
                     to='college.Class')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='SectionResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_learning.sectionresource_set+',
                     to='contenttypes.contenttype')),
                ('section',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='resources',
                     to='learning.section')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='SectionWebResource',
            fields=[
                ('sectionresource_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='learning.sectionresource')),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('learning.sectionresource',),
        ),
        migrations.CreateModel(
            name='Subarea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(max_length=1024, verbose_name='descrição')),
                ('image',
                 models.ImageField(
                     blank=True,
                     null=True,
                     upload_to=learning.models.subarea_pic_path,
                     verbose_name='imagem')),
                ('img_url', models.TextField(blank=True, null=True, verbose_name='imagem (url)')),
                ('area',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='subareas',
                     to='learning.area')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='SectionSubsection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('parent',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='children_intermediary',
                     to='learning.section')),
                ('section',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='parents_intermediary',
                     to='learning.section')),
            ],
            options={
                'ordering': ('parent', 'index'),
                'unique_together': {('section', 'parent'), ('index', 'parent')},
            },
        ),
        migrations.CreateModel(
            name='SectionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('previous_content', models.TextField(blank=True, null=True)),
                ('author',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='_section_logs',
                     to=settings.AUTH_USER_MODEL)),
                ('section',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='log_entries',
                     to='learning.section')),
            ],
        ),
        migrations.AddField(
            model_name='section',
            name='parents',
            field=models.ManyToManyField(
                blank=True,
                related_name='children',
                through='learning.SectionSubsection',
                to='learning.Section',
                verbose_name='parents'),
        ),
        migrations.AddField(
            model_name='section',
            name='requirements',
            field=models.ManyToManyField(
                blank=True,
                related_name='required_by',
                to='learning.Section',
                verbose_name='requisitos'),
        ),
        migrations.AddField(
            model_name='section',
            name='subarea',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='sections',
                to='learning.subarea',
                verbose_name='subarea'),
        ),
        migrations.CreateModel(
            name='Question',
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
                ('content', markdownx.models.MarkdownxField()),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('edit_timestamp', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=128)),
                ('decided_answer',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='answered_question',
                     to='learning.answer')),
                ('deciding_teacher',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='answered_questions_teacher',
                     to=settings.AUTH_USER_MODEL)),
                ('duplication_of',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='duplicates',
                     to='learning.question')),
                ('linked_classes',
                 models.ManyToManyField(
                     blank=True,
                     related_name='linked_questions',
                     to='college.Class',
                     verbose_name='Unidades curriculares relacionadas')),
                ('linked_exercises',
                 models.ManyToManyField(
                     blank=True,
                     related_name='linked_questions',
                     to='learning.Exercise',
                     verbose_name='Exercícios relacionados')),
                ('linked_sections',
                 models.ManyToManyField(
                     blank=True,
                     related_name='linked_questions',
                     to='learning.Section',
                     verbose_name='Secções relacionadas')),
                ('teacher_decided_answer',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='answered_question_teacher',
                     to='learning.answer')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.activity', models.Model),
        ),
        migrations.AddField(
            model_name='exercise',
            name='synopses_sections',
            field=models.ManyToManyField(
                blank=True,
                related_name='exercises',
                to='learning.Section',
                verbose_name='secções de sínteses'),
        ),
        migrations.AddField(
            model_name='classsection',
            name='section',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='classes_rel',
                to='learning.section'),
        ),
        migrations.CreateModel(
            name='AnswerNotification',
            fields=[
                ('notification_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.notification')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.answer')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.notification',),
        ),
        migrations.AddField(
            model_name='answer',
            name='to',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='answers',
                to='learning.question'),
        ),
        migrations.CreateModel(
            name='SectionSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('url', models.URLField(blank=True, null=True, verbose_name='endereço')),
                ('section',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='sources',
                     to='learning.section')),
            ],
            options={
                'ordering': ('section', 'title', 'url'),
                'unique_together': {('section', 'url')},
            },
        ),
        migrations.CreateModel(
            name='SectionDocumentResource',
            fields=[
                ('sectionresource_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='learning.sectionresource')),
                ('document',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='section_resources',
                     to='documents.document')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('learning.sectionresource',),
        ),
        migrations.AlterUniqueTogether(
            name='classsection',
            unique_together={('index', 'corresponding_class'), ('section', 'corresponding_class')},
        ),
    ]
