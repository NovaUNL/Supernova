import college.models
import django.contrib.gis.db.models.fields
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):
    replaces = [
        ('college', '0001_initial'), ('college', '0002_auto_20200323_1231'),
        ('college', '0003_auto_20200706_0113'), ('college', '0004_auto_20200714_1254'),
        ('college', '0005_auto_20200803_0303'), ('college', '0006_auto_20200817_0303'),
        ('college', '0007_auto_20200823_0112'), ('college', '0008_teacher_user'),
        ('college', '0009_auto_20200921_0012'), ('college', '0010_auto_20201004_1604'),
        ('college', '0011_auto_20201004_1655'), ('college', '0012_auto_20201005_0204'),
        ('college', '0013_auto_20201005_2229'), ('college', '0014_auto_20201005_2305'),
        ('college', '0015_academicdatachange'), ('college', '0016_auto_20201006_0416'),
        ('college', '0017_auto_20201006_1423'), ('college', '0018_auto_20201008_1701'),
        ('college', '0019_auto_20201010_0437'), ('college', '0020_auto_20201010_0525'),
        ('college', '0021_auto_20201010_0611'), ('college', '0022_auto_20201010_1910'),
        ('college', '0023_auto_20201011_2248'), ('college', '0024_auto_20201012_0605'),
        ('college', '0025_auto_20201012_0915'), ('college', '0026_teacher_file_consent'),
        ('college', '0027_auto_20201018_2200'), ('college', '0028_auto_20201018_2344'),
        ('college', '0029_auto_20201019_0116'), ('college', '0030_auto_20201109_0332'),
        ('college', '0031_auto_20201117_0355'), ('college', '0032_auto_20201227_0018')
    ]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('abbreviation', models.CharField(db_index=True, max_length=16, null=True, unique=True)),
                ('map_tag', models.CharField(max_length=20, unique=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=college.models.building_pic_path)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256)),
                ('abbreviation', models.CharField(default='---', max_length=16)),
                ('description', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('credits', models.IntegerField(blank=True, null=True)),
                ('extinguished', models.BooleanField(default=False)),
                ('url', models.URLField(blank=True, max_length=256, null=True)),
                ('avg_grade', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'classes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ClassFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('category', models.IntegerField(
                    choices=[
                        (2, 'Slides'), (3, 'Problemas'), (4, 'Protolos'), (5, 'Seminário'),
                        (6, 'Exame'), (7, 'Teste'), (8, 'Suporte'), (9, 'Outros')])),
                ('visibility',
                 models.IntegerField(
                     choices=[(0, 'Todos'), (1, 'Estudantes'), (2, 'Inscritos'), (3, 'Ninguém')],
                     default=3)),
                ('official', models.BooleanField(default=False)),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('period', models.IntegerField(
                    choices=[
                        (1, 'Anual'), (2, '1º semestre'), (3, '2º semestre'),
                        (4, '1º trimestre'), (5, '2º trimestre'), (6, '3º trimestre'), (7, '4º trimestre')])),
                ('year', models.IntegerField()),
                ('information', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('visibility',
                 models.IntegerField(
                     choices=[(0, 'Todos'), (1, 'Estudantes'), (2, 'Inscritos'), (3, 'Ninguém')],
                     default=1)),
                ('avg_grade', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassInstanceAnnouncement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('title', models.CharField(max_length=256)),
                ('message', models.TextField()),
                ('datetime', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassInstanceEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('date', models.DateField()),
                ('time', models.TimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('type',
                 models.IntegerField(
                     choices=[
                         (1, 'Teste'), (2, 'Exame'), (3, 'Discussão'), (4, 'Viagem'), (5, 'Enúnciação'),
                         (6, 'Entrega'), (7, 'Aula'), (8, 'Apresentação'), (9, 'Seminário'), (10, 'Palestra')],
                     null=True)),
                ('season',
                 models.IntegerField(
                     choices=[(1, 'Epoca normal'), (2, 'Epoca de exame'), (3, 'Epoca especial')],
                     null=True)),
                ('info', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256)),
                ('abbreviation', models.CharField(blank=True, max_length=128, null=True)),
                ('description', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('degree',
                 models.IntegerField(
                     choices=[
                         (1, 'Licenciatura'), (2, 'Mestrado'), (3, 'Doutoramento'), (4, 'Mestrado Integrado'),
                         (5, 'Pos-Graduação'), (6, 'Estudos Avançados'), (7, 'Pré-Graduação')])),
                ('active', models.BooleanField(default=False)),
                ('url', models.URLField(blank=True, max_length=256, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_type', models.CharField(blank=True, max_length=1, null=True)),
                ('period', models.IntegerField(blank=True, null=True)),
                ('year', models.IntegerField()),
                ('required', models.BooleanField()),
            ],
            options={
                'ordering': ['year', 'period_type', 'period'],
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('description', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('extinguished', models.BooleanField(default=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=college.models.department_pic_path)),
                ('url', models.URLField(blank=True, max_length=256, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('attendance', models.BooleanField(null=True)),
                ('attendance_date', models.DateField(blank=True, null=True)),
                ('normal_grade', models.IntegerField(blank=True, null=True)),
                ('normal_grade_date', models.DateField(blank=True, null=True)),
                ('recourse_grade', models.IntegerField(blank=True, null=True)),
                ('recourse_grade_date', models.DateField(blank=True, null=True)),
                ('special_grade', models.IntegerField(blank=True, null=True)),
                ('special_grade_date', models.DateField(blank=True, null=True)),
                ('approved', models.BooleanField(blank=True, null=True)),
                ('grade', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('hash', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('size', models.IntegerField()),
                ('mime', models.CharField(max_length=256, null=True)),
                ('name', models.CharField(max_length=256, null=True)),
                ('extension', models.CharField(max_length=16, null=True)),
                ('external', models.BooleanField(default=False)),
                ('license',
                 models.IntegerField(
                     blank=True,
                     choices=[(0, 'Todos os direitos reservados'), (1, 'Domínio Público'),
                              (2, 'GPLv3'), (3, 'MIT'), (4, 'BSD'),
                              (5, 'Creative Commons BY'), (6, 'Creative Commons BY-SA'),
                              (7, 'Creative Commons BY-NC'), (8, 'Creative Commons BY-SA-NC'),
                              (100, 'Permissiva genérica')],
                     default=0,
                     null=True)),
                ('license_str', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('author_str', models.CharField(blank=True, max_length=256, null=True)),
                ('doi', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('floor', models.IntegerField(default=0)),
                ('unlocked', models.BooleanField(default=None, null=True)),
                ('location',
                 django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=college.models.place_pic_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlaceFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.FileField(upload_to=college.models.feature_pic_path)),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('shift_type', models.IntegerField(
                    choices=[
                        (1, 'Teórico'), (2, 'Prático'), (3, 'Teórico-pratico'), (4, 'Seminário'),
                        (5, 'Orientação tutorial'), (6, 'Trabalho de campo'), (7, 'Teórico Online'),
                        (8, 'Prático Online'), (9, 'Teórico-Pratico Online')])),
                ('number', models.IntegerField()),
                ('required', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShiftInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('recurring', models.BooleanField(default=True)),
                ('weekday',
                 models.IntegerField(
                     blank=True,
                     choices=[
                         (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'),
                         (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo')],
                     null=True)),
                ('start', models.IntegerField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['weekday', 'start'],
            },
        ),
        migrations.CreateModel(
            name='ShiftStudents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'shift students',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200, null=True)),
                ('number', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('abbreviation', models.CharField(blank=True, db_index=True, max_length=64, null=True)),
                ('graduation_grade', models.IntegerField(blank=True, default=None, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('first_year', models.IntegerField(blank=True, null=True)),
                ('last_year', models.IntegerField(blank=True, null=True)),
                ('credits', models.IntegerField(blank=True, null=True)),
                ('avg_grade', models.FloatField(blank=True, null=True)),
            ],
            options={
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='TeacherRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('place_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='college.place')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('door_number', models.IntegerField(blank=True, null=True)),
                ('type',
                 models.IntegerField(
                     choices=[(1, 'Genérico'), (2, 'Sala de aula'), (3, 'Auditório'), (4, 'Laboratório'),
                              (5, 'Sala de computadores'), (6, 'Sala de reuniões'), (7, 'Sala de mestrados'),
                              (8, 'Gabinete')],
                     default=0)),
                ('description', models.TextField(blank=True, null=True)),
                ('equipment', models.TextField(blank=True, null=True)),
                ('extinguished', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('floor', 'door_number', 'name'),
            },
            bases=('college.place', models.Model),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField(blank=True, db_index=True, null=True, unique=True)),
                ('iid', models.CharField(blank=True, max_length=64, null=True)),
                ('external_update', models.DateTimeField(blank=True, null=True)),
                ('frozen', models.BooleanField(default=False)),
                ('disappeared', models.BooleanField(default=False)),
                ('external_data', models.JSONField(blank=True, default=dict, null=True)),
                ('last_save', models.DateTimeField(auto_now=True)),
                ('name', models.TextField(db_index=True, max_length=200)),
                ('first_year', models.IntegerField(blank=True, null=True)),
                ('last_year', models.IntegerField(blank=True, null=True)),
                ('abbreviation', models.CharField(blank=True, db_index=True, max_length=64, null=True)),
                ('url', models.URLField(blank=True, max_length=256, null=True)),
                ('email', models.EmailField(blank=True, max_length=256, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=college.models.teacher_pic_path)),
                ('file_consent',
                 models.IntegerField(
                     blank=True,
                     choices=[(0, 'Todos'), (1, 'Estudantes'), (2, 'Inscritos'), (3, 'Ninguém')],
                     default=None,
                     null=True)),
                ('departments', models.ManyToManyField(related_name='teachers', to='college.Department')),
                ('rank',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     to='college.teacherrank')),
                ('same_as',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     to='college.teacher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
