from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    replaces = [('supernova', '0001_initial'), ('supernova', '0002_changelognotification'), ('supernova', '0003_auto_20201008_1701'), ('supernova', '0004_supportpledge'), ('supernova', '0005_supportpledge_comment')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Catchphrase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrase', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', markdownx.models.MarkdownxField()),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
