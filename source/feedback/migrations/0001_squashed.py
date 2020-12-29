from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('feedback', '0001_initial'), ('feedback', '0002_auto_20201010_2107'),
                ('feedback', '0003_auto_20201011_0553'), ('feedback', '0004_auto_20201014_1143'),
                ('feedback', '0005_remove_vote_to'), ('feedback', '0006_auto_20201111_0604'),
                ('feedback', '0007_suggestion'), ('feedback', '0008_auto_20201112_0434'),
                ('feedback', '0009_auto_20201227_2031')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('information', models.TextField()),
            ],
        ),
    ]
