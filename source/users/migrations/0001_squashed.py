import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
from django.db import migrations
import django.utils.timezone
import markdownx.models
import users.models


class Migration(migrations.Migration):
    replaces = [('users', '0001_initial'), ('users', '0002_auto_20200314_0129'),
                ('users', '0003_auto_20200802_2311'), ('users', '0004_auto_20200808_0457'),
                ('users', '0005_auto_20200823_0107'), ('users', '0006_auto_20200905_0409'),
                ('users', '0007_activity_user'), ('users', '0008_auto_20200919_0303'),
                ('users', '0009_auto_20200919_0324'), ('users', '0010_auto_20200920_1352'),
                ('users', '0011_user_course'), ('users', '0012_auto_20200925_1940'),
                ('users', '0013_reputationoffset_reputationoffsetnotification'), ('users', '0014_auto_20201008_1701'),
                ('users', '0015_auto_20201010_2107'), ('users', '0016_auto_20201011_2257'),
                ('users', '0017_auto_20201015_0559'), ('users', '0018_auto_20201111_0604'),
                ('users', '0019_subscription'), ('users', '0020_auto_20201117_0355'),
                ('users', '0021_auto_20201215_1203'), ('users', '0022_auto_20201227_0409')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('college', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='VulnerableHash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.TextField()),
            ],
            options={
                'db_table': 'Hashes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser',
                 models.BooleanField(
                     default=False,
                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                     verbose_name='superuser status')),
                ('username',
                 models.CharField(
                     error_messages={'unique': 'A user with that username already exists.'},
                     help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                     max_length=150, unique=True,
                     validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                     verbose_name='username')),
                ('first_name',
                 models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff',
                 models.BooleanField(
                     default=False,
                     help_text='Designates whether the user can log into this admin site.',
                     verbose_name='staff status')),
                ('is_active',
                 models.BooleanField(
                     default=True,
                     help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                     verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nickname', models.CharField(db_index=True, max_length=20, unique=True, verbose_name='Alcunha')),
                ('last_nickname_change', models.DateField(default=datetime.date(2000, 1, 1))),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Nascimento')),
                ('last_activity', models.DateTimeField(auto_now_add=True)),
                ('residence', models.CharField(blank=True, max_length=64, null=True, verbose_name='Residência')),
                ('picture',
                 models.ImageField(
                     blank=True,
                     null=True,
                     upload_to=users.models.user_profile_pic_path,
                     verbose_name='Foto')),
                ('webpage', models.URLField(blank=True, null=True, verbose_name='Página pessoal')),
                ('profile_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('info_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('about_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('social_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('groups_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('enrollments_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('schedule_visibility',
                 models.IntegerField(
                     choices=[(0, 'Ninguém'), (1, 'Amigos'), (2, 'Utilizadores'), (3, 'Todos')],
                     default=0)),
                ('gender',
                 models.IntegerField(blank=True, choices=[(0, 'Homem'), (1, 'Mulher'), (2, 'Outro')], null=True)),
                ('about', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('permissions_overridden', models.BooleanField(default=False)),
                ('is_student', models.BooleanField(default=False)),
                ('is_teacher', models.BooleanField(default=False)),
                ('points', models.IntegerField(default=0)),
                ('course',
                 models.ForeignKey(
                     blank=True,
                     default=None,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to='college.course')),
                ('groups',
                 models.ManyToManyField(
                     blank=True,
                     help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                     related_name='user_set',
                     related_query_name='user',
                     to='auth.Group',
                     verbose_name='groups')),
                ('user_permissions',
                 models.ManyToManyField(
                     blank=True,
                     help_text='Specific permissions for this user.',
                     related_name='user_set',
                     related_query_name='user',
                     to='auth.Permission',
                     verbose_name='user permissions')),
            ],
            options={
                'permissions': [
                    ('student_access', 'Can browse the system as a student.'),
                    ('teacher_access', 'Can browse the system as a teacher.')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('style', models.CharField(default=None, max_length=15, null=True)),
                ('points', models.IntegerField(default=0)),
                ('picture', models.ImageField(null=True, upload_to=users.models.award_pic_path)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_timestamp', models.DateTimeField(auto_now_add=True)),
                ('dismissed', models.BooleanField(default=False)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_users.notification_set+',
                     to='contenttypes.contenttype')),
                ('receiver',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='notifications',
                     to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='ScheduleEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('note', models.TextField(blank=True, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_users.scheduleentry_set+',
                     to='contenttypes.contenttype')),
                ('user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='schedule_entries',
                     to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'schedule entries',
            },
        ),
        migrations.CreateModel(
            name='GenericNotification',
            fields=[
                ('notification_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.notification')),
                ('message', models.TextField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects'
            },
            bases=('users.notification',),
        ),
        migrations.CreateModel(
            name='ScheduleOnce',
            fields=[
                ('scheduleentry_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.scheduleentry')),
                ('datetime', models.DateTimeField()),
                ('duration', models.IntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.scheduleentry',),
        ),
        migrations.CreateModel(
            name='SchedulePeriodic',
            fields=[
                ('scheduleentry_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.scheduleentry')),
                ('weekday', models.IntegerField(
                    choices=[
                        (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'),
                        (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo')])),
                ('time', models.TimeField()),
                ('duration', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.scheduleentry',),
        ),
        migrations.CreateModel(
            name='UserAward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receive_date', models.DateField(auto_created=True)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.award')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReputationOffset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_timestamp', models.DateTimeField(auto_now_add=True)),
                ('amount', models.IntegerField()),
                ('reason', models.CharField(max_length=300, null=True)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_users.reputationoffset_set+',
                     to='contenttypes.contenttype')),
                ('receiver',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_offsets',
                                   to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('username', models.CharField(max_length=128, verbose_name='utilizador')),
                ('nickname', models.CharField(blank=True, max_length=128, verbose_name='alcunha')),
                ('password', models.CharField(max_length=128, verbose_name='palavra-passe')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(max_length=16)),
                ('failed_attempts', models.IntegerField(default=0)),
                ('requested_student',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='registrations',
                     to='college.student')),
                ('requested_teacher',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='registrations',
                     to='college.teacher')),
                ('resulting_user',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=16, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expiration', models.DateTimeField()),
                ('revoked', models.BooleanField(default=False)),
                ('issuer',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='invites',
                     to=settings.AUTH_USER_MODEL)),
                ('registration',
                 models.OneToOneField(
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     to='users.registration')),
                ('resulting_user',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform',
                 models.IntegerField(
                     blank=True,
                     choices=[
                         (0, 'GitLab'), (1, 'GitHub'), (3, 'Mastodon'), (4, 'Diaspora'), (5, 'Peertube'), (6, 'Vimeo'),
                         (7, 'DeviantArt'), (8, 'Flickr'), (9, 'Thingiverse'), (10, 'Wikipedia'), (1000, 'Outro')],
                     null=True)),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('url', models.URLField(max_length=128, unique=True)),
                ('user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='external_pages',
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='award',
            name='users',
            field=models.ManyToManyField(related_name='awards', through='users.UserAward', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('activity_id', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_users.activity_set+',
                     to='contenttypes.contenttype')),
                ('user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='activities',
                     to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_object_id', models.PositiveIntegerField()),
                ('issue_timestamp', models.DateTimeField(auto_now_add=True)),
                ('subscriber',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='subscriptions',
                     to=settings.AUTH_USER_MODEL)),
                ('to_content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'unique_together': {('to_content_type', 'to_object_id', 'subscriber')},
            },
        ),
        migrations.CreateModel(
            name='ReputationOffsetNotification',
            fields=[
                ('notification_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.notification')),
                ('reputation_offset',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.reputationoffset')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.notification',),
        ),
    ]
