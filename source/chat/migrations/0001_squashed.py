from django.conf import settings
from django.db import migrations, models
import django.utils.timezone
import markdownx.models


class Migration(migrations.Migration):
    replaces = [
        ('chat', '0001_initial'),
        ('chat', '0002_auto_20201114_1741'),
        ('chat', '0003_auto_20201116_1909'),
        ('chat', '0004_auto_20201117_0355'),
        ('chat', '0005_auto_20201209_1935'),
        ('chat', '0006_auto_20201210_0100')
    ]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('groups', '0001_squashed'),
        ('users', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='creator',
                    to=settings.AUTH_USER_MODEL)),
                ('last_activity_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='_conversation_last_messages',
                     to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_chat.conversation_set+',
                     to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='DMChat',
            fields=[
                ('conversation_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='chat.conversation')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('chat.conversation',),
        ),
        migrations.CreateModel(
            name='PrivateRoom',
            fields=[
                ('conversation_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='chat.conversation')),
                ('name', models.CharField(db_index=True, max_length=100)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('chat.conversation',),
        ),
        migrations.CreateModel(
            name='PublicRoom',
            fields=[
                ('conversation_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='chat.conversation')),
                ('identifier', models.CharField(db_index=True, max_length=32, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('anonymous_allowed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('chat.conversation',),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('last_message_edition', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('conversation',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='messages',
                     to='chat.conversation')),
            ],
            options={
                'unique_together': {('author', 'creation', 'content', 'conversation')},
            },
        ),
        migrations.CreateModel(
            name='ConversationUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'conversation',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.conversation')),
                ('last_read_message',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     to='chat.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='conversation',
            name='users',
            field=models.ManyToManyField(through='chat.ConversationUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('activity_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='users.activity')),
                ('to_object_id', models.PositiveIntegerField()),
                ('content', markdownx.models.MarkdownxField()),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('edit_timestamp', models.DateTimeField(auto_now_add=True)),
                ('to_content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('users.activity',),
        ),
        migrations.CreateModel(
            name='GroupInternalConversation',
            fields=[
                ('conversation_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='chat.conversation')),
                ('title', models.CharField(max_length=100)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='groups.group')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('chat.conversation',),
        ),
        migrations.CreateModel(
            name='GroupExternalConversation',
            fields=[
                ('conversation_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='chat.conversation')),
                ('title', models.CharField(max_length=100)),
                ('public', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=False)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='groups.group')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('chat.conversation',),
        ),
    ]
