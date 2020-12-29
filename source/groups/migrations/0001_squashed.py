from django.db import migrations, models
import groups.models
import markdownx.models


class Migration(migrations.Migration):
    replaces = [
        ('groups', '0001_initial'), ('groups', '0002_auto_20200323_0233'),
        ('groups', '0003_auto_20200323_0745'), ('groups', '0004_auto_20200323_0818'),
        ('groups', '0005_auto_20200323_1231'), ('groups', '0006_group_official'),
        ('groups', '0007_auto_20200918_1952'), ('groups', '0008_auto_20200918_2059'),
        ('groups', '0009_auto_20200920_1352'), ('groups', '0010_auto_20201110_2319'),
        ('groups', '0011_auto_20201111_0457'), ('groups', '0012_auto_20201112_0549'),
        ('groups', '0013_auto_20201117_0355'), ('groups', '0014_auto_20201210_0737'),
        ('groups', '0015_auto_20201210_1105'), ('groups', '0016_membership_datetime')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', markdownx.models.MarkdownxField()),
                ('start_date', models.DateField()),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('enroll_here', models.BooleanField(default=True)),
                ('cost', models.IntegerField()),
                ('type',
                 models.IntegerField(
                     choices=[
                         (0, 'Genérico'), (1, 'Palestra'), (2, 'Workshop'), (3, 'Festa'),
                         (4, 'Concurso'), (5, 'Feira'), (6, 'Encontro')])),
            ],
        ),
        migrations.CreateModel(
            name='EventUserQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('awaiting_payment', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('index', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GalleryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.TextField(blank=True, null=True)),
                ('item_datetime', models.DateTimeField(auto_now_add=True)),
                ('index', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(db_index=True, max_length=64, unique=True)),
                ('name', models.CharField(max_length=65)),
                ('description', markdownx.models.MarkdownxField(blank=True, null=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to=groups.models.group_icon_path)),
                ('image', models.ImageField(blank=True, null=True, upload_to=groups.models.group_image_path)),
                ('type',
                 models.IntegerField(
                     choices=[
                         (0, 'Intitucional'), (1, 'Núcleo'), (2, 'Associação'),
                         (3, 'Pedagógico'), (4, 'CoPe'), (5, 'Comunidade')])),
                ('outsiders_openness',
                 models.IntegerField(
                     choices=[(0, 'Secreto'), (1, 'Fechado'), (2, 'Pedido'), (3, 'Aberta')],
                     default=0)),
                ('official', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
