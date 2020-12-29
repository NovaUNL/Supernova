from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    replaces = [
        ('supernova', '0001_initial'), ('supernova', '0002_changelognotification'),
        ('supernova', '0003_auto_20201008_1701'), ('supernova', '0004_supportpledge'),
        ('supernova', '0005_supportpledge_comment')]

    initial = True

    dependencies = [
        ('users', '0001_squashed'),
        ('supernova', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportPledge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pledge_towards', models.IntegerField(
                    choices=[(0, 'Independente'), (1, 'Independente com suporte'), (2, 'Associado em complemento'),
                             (3, 'Associado para substituição')])),
                ('anonymous', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pledge',
                                              to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChangelogNotification',
            fields=[
                ('notification_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='users.notification')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supernova.changelog')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.notification',),
        ),
    ]
