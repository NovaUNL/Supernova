from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models
import news.models


class Migration(migrations.Migration):

    replaces = [('news', '0001_initial'), ('news', '0002_auto_20201227_0538')]

    initial = True

    dependencies = [
        ('users', '0001_squashed'),
        ('news', '0001_squashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='pinnednewsitem',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='authored_pinned_item',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pinnednewsitem',
            name='edit_author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='edited_pinned_item',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newsvote',
            name='news_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.newsitem'),
        ),
        migrations.AddField(
            model_name='newsvote',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='authored_news_items',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='edit_author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='edited_news_items',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='tags',
            field=models.ManyToManyField(blank=True, to='news.NewsTag'),
        ),
        migrations.AlterUniqueTogether(
            name='newsitem',
            unique_together={('title', 'datetime')},
        ),
    ]
