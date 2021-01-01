from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('college', '0002_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurricularComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_id', models.CharField(blank=True, db_index=True, max_length=100, null=True, unique=True)),
                ('min_year', models.IntegerField(default=0)),
                ('min_period',
                 models.IntegerField(
                     blank=True,
                     choices=[
                         (1, 'Anual'), (2, '1º semestre'), (3, '2º semestre'),
                         (4, '1º trimestre'), (5, '2º trimestre'), (6, '3º trimestre'), (7, '4º trimestre')],
                     default=None,
                     null=True)),
                ('suggested_year', models.IntegerField(blank=True, null=True)),
                ('suggested_period',
                 models.IntegerField(
                     blank=True,
                     choices=[
                         (1, 'Anual'), (2, '1º semestre'), (3, '2º semestre'),
                         (4, '1º trimestre'), (5, '2º trimestre'), (6, '3º trimestre'), (7, '4º trimestre')],
                     null=True)),
                ('required', models.BooleanField(default=True)),
                ('aggregation', models.JSONField(blank=True, default=dict)),
                ('polymorphic_ctype',
                 models.ForeignKey(
                     editable=False,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='polymorphic_college.curricularcomponent_set+',
                     to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['suggested_year', 'suggested_period'],
            },
        ),
        migrations.CreateModel(
            name='CurricularBlockComponent',
            fields=[
                ('curricularcomponent_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='college.curricularcomponent')),
                ('name', models.CharField(max_length=100)),
                ('min_components', models.IntegerField(default=0)),
                ('min_credits', models.IntegerField(default=0)),
                ('suggested_credits', models.IntegerField(blank=True, null=True)),
                ('children', models.ManyToManyField(related_name='parents', to='college.CurricularComponent')),
            ],
            options={
                'abstract': False,
            },
            bases=('college.curricularcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='CurricularBlockVariantComponent',
            fields=[
                ('curricularcomponent_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='college.curricularcomponent')),
                ('name', models.CharField(max_length=100)),
                ('min_components', models.IntegerField(default=0)),
                ('min_credits', models.IntegerField(default=0)),
                ('suggested_credits', models.IntegerField(blank=True, null=True)),
                ('block',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='block_variants',
                     to='college.curricularblockcomponent')),
                ('blocked_components',
                 models.ManyToManyField(related_name='curricular_blocks', to='college.CurricularComponent')),
            ],
            options={
                'abstract': False,
            },
            bases=('college.curricularcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='CurricularClassComponent',
            fields=[
                ('curricularcomponent_ptr',
                 models.OneToOneField(
                     auto_created=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     parent_link=True,
                     primary_key=True,
                     serialize=False,
                     to='college.curricularcomponent')),
                ('klass',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='curricular_components',
                     to='college.class')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('college.curricularcomponent',),
        ),
        migrations.DeleteModel(
            name='Curriculum',
        ),
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_year', models.IntegerField(blank=True, null=True)),
                ('to_year', models.IntegerField(blank=True, null=True)),
                ('aggregation', models.JSONField(default=dict)),
                ('course',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='curriculums',
                     to='college.course')),
                ('root',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='curriculums',
                     to='college.curricularblockcomponent')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='curriculum',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='courses',
                to='college.curriculum'),
        ),
    ]
