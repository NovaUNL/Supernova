from django.conf import settings
from django.db import migrations, models
from django.db import migrations
import django.db.models.deletion
import django.utils.timezone
import groups.models
import markdownx.models


class Migration(migrations.Migration):
    replaces = [('groups', '0001_initial'), ('groups', '0002_auto_20200323_0233'),
                ('groups', '0003_auto_20200323_0745'), ('groups', '0004_auto_20200323_0818'),
                ('groups', '0005_auto_20200323_1231'), ('groups', '0006_group_official'),
                ('groups', '0007_auto_20200918_1952'), ('groups', '0008_auto_20200918_2059'),
                ('groups', '0009_auto_20200920_1352'), ('groups', '0010_auto_20201110_2319'),
                ('groups', '0011_auto_20201111_0457'), ('groups', '0012_auto_20201112_0549'),
                ('groups', '0013_auto_20201117_0355'), ('groups', '0014_auto_20201210_0737'),
                ('groups', '0015_auto_20201210_1105'), ('groups', '0016_membership_datetime')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0001_squashed'),
        ('college', '0001_squashed'),
        ('groups', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=128, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('group',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='schedule_entries',
                     to='groups.group')),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False, null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_groups.scheduleentry_set+',
                     to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name_plural': 'schedule entries',
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='groups.activity')),
                ('title', models.CharField(max_length=256)),
                ('content', markdownx.models.MarkdownxField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
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
                     to='groups.scheduleentry')),
                ('datetime', models.DateTimeField()),
                ('duration', models.IntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.scheduleentry',),
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
                     to='groups.scheduleentry')),
                ('weekday',
                 models.IntegerField(
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
            bases=('groups.scheduleentry',),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_admin', models.BooleanField(default=False)),
                ('can_modify_roles', models.BooleanField(default=False)),
                ('can_assign_roles', models.BooleanField(default=False)),
                ('can_announce', models.BooleanField(default=False)),
                ('can_read_conversations', models.BooleanField(default=False)),
                ('can_write_conversations', models.BooleanField(default=False)),
                ('can_read_internal_conversations', models.BooleanField(default=False)),
                ('can_write_internal_conversations', models.BooleanField(default=False)),
                ('can_read_internal_documents', models.BooleanField(default=False)),
                ('can_write_internal_documents', models.BooleanField(default=False)),
                ('can_write_public_documents', models.BooleanField(default=False)),
                ('can_change_schedule', models.BooleanField(default=False)),
                ('group',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='roles',
                     to='groups.group')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('since', models.DateTimeField(auto_now_add=True)),
                ('group',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='memberships',
                     to='groups.group')),
                ('member',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='memberships',
                     to=settings.AUTH_USER_MODEL)),
                ('role',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='memberships',
                     to='groups.role')),
            ],
            options={
                'unique_together': {('group', 'member')},
            },
        ),
        migrations.CreateModel(
            name='GroupActivityNotification',
            fields=[
                ('notification_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.notification')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.activity')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.notification',),
        ),
        migrations.AddField(
            model_name='group',
            name='default_role',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='default_to',
                to='groups.role'),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(
                related_name='groups_custom',
                through='groups.Membership',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='group',
            name='place',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='groups',
                to='college.place'),
        ),
        migrations.AddField(
            model_name='galleryitem',
            name='gallery',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='items',
                to='groups.gallery'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='galleries',
                to='groups.group'),
        ),
        migrations.AddField(
            model_name='eventuserqueue',
            name='event',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='queue_positions',
                to='groups.event'),
        ),
        migrations.AddField(
            model_name='eventuserqueue',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='event_queue_positions',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='attended_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='events',
                to='groups.group'),
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='events',
                to='college.place'),
        ),
        migrations.AddField(
            model_name='event',
            name='queued',
            field=models.ManyToManyField(
                related_name='queued_events',
                through='groups.EventUserQueue',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='subscribers',
            field=models.ManyToManyField(related_name='event_subscription', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activity',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='group_activity',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activity',
            name='group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='activities',
                to='groups.group'),
        ),
        migrations.AddField(
            model_name='activity',
            name='polymorphic_ctype',
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='polymorphic_groups.activity_set+',
                to='contenttypes.contenttype'),
        ),
        migrations.CreateModel(
            name='ScheduleSuspension',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='groups.activity')),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, default=None, null=True)),
                ('entry',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='suspensions',
                     to='groups.scheduleperiodic')),
                ('replacement',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='replaced_suspended_entries',
                     to='groups.scheduleentry')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
        ),
        migrations.CreateModel(
            name='ScheduleRevoke',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='groups.activity')),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
                ('entry',
                 models.OneToOneField(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='revocation',
                     to='groups.scheduleentry')),
                ('replacement',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='replaced_revoked_entries',
                     to='groups.scheduleentry')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
        ),
        migrations.CreateModel(
            name='ScheduleCreation',
            fields=[
                ('activity_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='groups.activity')),
                ('entry',
                 models.OneToOneField(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='creation',
                     to='groups.scheduleentry')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
        ),
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('granted', models.BooleanField(blank=True, default=None, null=True)),
                ('message', models.TextField(blank=True, default=None, max_length=1000, null=True)),
                ('group',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='membership_requests',
                     to='groups.group')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='membership_requests',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'group')},
            },
        ),
        migrations.CreateModel(
            name='GalleryUpload',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='groups.activity')),
                ('item',
                 models.OneToOneField(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='upload',
                     to='groups.galleryitem')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
        ),
        migrations.CreateModel(
            name='EventAnnouncement',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='groups.activity')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='groups.event')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('groups.activity',),
        ),
    ]
