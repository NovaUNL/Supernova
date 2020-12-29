from django.db import migrations, models
import markdownx.models
import news.models


class Migration(migrations.Migration):

    replaces = [('news', '0001_initial'), ('news', '0002_auto_20201227_0538')]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('summary', models.TextField(max_length=300)),
                ('content', markdownx.models.MarkdownxField()),
                ('datetime', models.DateTimeField()),
                ('edited', models.BooleanField(default=False)),
                ('edit_note', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('edit_datetime', models.DateTimeField(blank=True, default=None, null=True)),
                ('source', models.URLField(blank=True, max_length=256, null=True)),
                ('cover_img',
                 models.ImageField(
                     blank=True,
                     max_length=256,
                     null=True,
                     upload_to=news.models.news_item_picture)),
                ('generated', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['datetime', 'title'],
            },
        ),
        migrations.CreateModel(
            name='NewsTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='NewsVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type',
                 models.IntegerField(choices=[(1, 'upvote'), (2, 'downvote'), (3, 'award'), (4, 'clickbait')])),
            ],
        ),
        migrations.CreateModel(
            name='PinnedNewsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('content', markdownx.models.MarkdownxField()),
                ('datetime', models.DateTimeField()),
                ('edit_datetime', models.DateTimeField(blank=True, default=None, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
