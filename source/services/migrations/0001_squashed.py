from django.db import migrations, models
import django.db.models.deletion
import services.models


class Migration(migrations.Migration):
    replaces = [
        ('services', '0001_initial'),
        ('services', '0002_auto_20200823_0116'),
        ('services', '0003_auto_20201020_0429')]

    initial = True

    dependencies = [
        ('college', '0001_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('abbreviation', models.CharField(max_length=64)),
                ('map_tag', models.CharField(max_length=15)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=services.models.service_pic_path)),
                ('type',
                 models.IntegerField(
                     choices=[
                         (0, 'Serviço académico'), (1, 'Restauração'), (2, 'Biblioteca'), (3, 'Reprografia'),
                         (4, 'Loja'), (5, 'Multibanco'), (6, 'Segurança'), (100, 'Outro')])),
                ('place',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='services',
                     to='college.place')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'place')},
            },
        ),
        migrations.CreateModel(
            name='ServiceScheduleEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(blank=True, max_length=128, null=True)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('weekday',
                 models.IntegerField(
                     choices=[
                         (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'),
                         (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo'), (7, 'Dias úteis')])),
                ('service',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='schedule',
                     to='services.service')),
            ],
            options={
                'verbose_name_plural': 'Service schedule entries',
                'ordering': ('service', 'weekday', 'start', 'designation'),
                'unique_together': {('service', 'weekday', 'start', 'designation')},
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('price', models.IntegerField()),
                ('has_stock', models.BooleanField(default=True)),
                ('category',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='products',
                     to='services.productcategory')),
                ('service',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='products',
                     to='services.service')),
            ],
            options={
                'ordering': ('service', 'category', 'name', 'price'),
                'unique_together': {('service', 'name')},
            },
        ),
        migrations.CreateModel(
            name='MealItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('date', models.DateField()),
                ('time',
                 models.IntegerField(
                     choices=[
                         (0, 'Pequeno-almoço'), (1, 'Lanche da manhã'), (2, 'Almoço'),
                         (3, 'Lanche da tarde'), (4, 'Jantar')])),
                ('meal_part_type',
                 models.IntegerField(
                     choices=[
                         (0, 'Sopa'), (1, 'Carne'), (2, 'Peixe'), (3, 'Vegetariano'), (4, 'Prato'),
                         (5, 'Sobremesa'), (6, 'Bebida'), (7, 'Menu')])),
                ('sugars', models.IntegerField(blank=True, null=True)),
                ('fats', models.IntegerField(blank=True, null=True)),
                ('proteins', models.IntegerField(blank=True, null=True)),
                ('calories', models.IntegerField(blank=True, null=True)),
                ('service',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='meal_items',
                     to='services.service')),
            ],
            options={
                'ordering': (),
                'unique_together': {('name', 'date', 'time', 'service', 'meal_part_type')},
            },
        ),
    ]
