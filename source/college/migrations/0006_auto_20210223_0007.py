from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('college', '0005_auto_20210126_0619'),
    ]

    operations = [
        migrations.AddField(
            model_name='classinstance',
            name='date_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='date_to',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='PeriodInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(
                    choices=[(1, 'Anual'), (2, '1º semestre'), (3, '2º semestre'), (4, '1º trimestre'),
                             (5, '2º trimestre'), (6, '3º trimestre'), (7, '4º trimestre')])),
                ('year', models.IntegerField()),
                ('date_from', models.DateField(blank=True, null=True)),
                ('date_to', models.DateField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('type', 'year')},
            },
        ),
        migrations.AddField(
            model_name='classinstance',
            name='period_instance',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='college.periodinstance'),
        ),
    ]
