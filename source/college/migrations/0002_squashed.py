import college.models
import django
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import markdownx.models


class Migration(migrations.Migration):
    replaces = [('college', '0001_initial'), ('college', '0002_auto_20200323_1231'),
                ('college', '0003_auto_20200706_0113'), ('college', '0004_auto_20200714_1254'),
                ('college', '0005_auto_20200803_0303'), ('college', '0006_auto_20200817_0303'),
                ('college', '0007_auto_20200823_0112'), ('college', '0008_teacher_user'),
                ('college', '0009_auto_20200921_0012'), ('college', '0010_auto_20201004_1604'),
                ('college', '0011_auto_20201004_1655'), ('college', '0012_auto_20201005_0204'),
                ('college', '0013_auto_20201005_2229'), ('college', '0014_auto_20201005_2305'),
                ('college', '0015_academicdatachange'), ('college', '0016_auto_20201006_0416'),
                ('college', '0017_auto_20201006_1423'), ('college', '0018_auto_20201008_1701'),
                ('college', '0019_auto_20201010_0437'), ('college', '0020_auto_20201010_0525'),
                ('college', '0021_auto_20201010_0611'), ('college', '0022_auto_20201010_1910'),
                ('college', '0023_auto_20201011_2248'), ('college', '0024_auto_20201012_0605'),
                ('college', '0025_auto_20201012_0915'), ('college', '0026_teacher_file_consent'),
                ('college', '0027_auto_20201018_2200'), ('college', '0028_auto_20201018_2344'),
                ('college', '0029_auto_20201019_0116'), ('college', '0030_auto_20201109_0332'),
                ('college', '0031_auto_20201117_0355'), ('college', '0032_auto_20201227_0018')]

    initial = True

    dependencies = [
        ('users', '0001_squashed'),
        ('college', '0001_squashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='teachers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='student',
            name='class_instances',
            field=models.ManyToManyField(through='college.Enrollment', to='college.ClassInstance'),
        ),
        migrations.AddField(
            model_name='student',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='students', to='college.course'),
        ),
        migrations.AddField(
            model_name='student',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.student'),
        ),
        migrations.AddField(
            model_name='student',
            name='shifts',
            field=models.ManyToManyField(through='college.ShiftStudents', to='college.Shift'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shiftstudents',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='college.shift'),
        ),
        migrations.AddField(
            model_name='shiftstudents',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='college.student'),
        ),
        migrations.AddField(
            model_name='shiftinstance',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.shiftinstance'),
        ),
        migrations.AddField(
            model_name='shiftinstance',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances',
                                    to='college.shift'),
        ),
        migrations.AddField(
            model_name='shift',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts',
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='shift',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.shift'),
        ),
        migrations.AddField(
            model_name='shift',
            name='students',
            field=models.ManyToManyField(through='college.ShiftStudents', to='college.Student'),
        ),
        migrations.AddField(
            model_name='shift',
            name='teachers',
            field=models.ManyToManyField(related_name='shifts', to='college.Teacher'),
        ),
        migrations.AddField(
            model_name='place',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='places', to='college.building'),
        ),
        migrations.AddField(
            model_name='place',
            name='features',
            field=models.ManyToManyField(blank=True, to='college.PlaceFeature'),
        ),
        migrations.AddField(
            model_name='file',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='file',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.file'),
        ),
        migrations.AddField(
            model_name='file',
            name='uploader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='files', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments',
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.enrollment'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments',
                                    to='college.student'),
        ),
        migrations.AddField(
            model_name='department',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='departments', to='college.building'),
        ),
        migrations.AddField(
            model_name='department',
            name='president',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='presided_departments', to='college.teacher'),
        ),
        migrations.AddField(
            model_name='department',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.department'),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='corresponding_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='college.class'),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='college.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='coordinated_courses', to='college.teacher'),
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='courses', to='college.department'),
        ),
        migrations.AddField(
            model_name='course',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.course'),
        ),
        migrations.AddField(
            model_name='classinstanceevent',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events',
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='classinstanceevent',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.classinstanceevent'),
        ),
        migrations.AddField(
            model_name='classinstanceannouncement',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='announcements',
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='classinstanceannouncement',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.classinstanceannouncement'),
        ),
        migrations.AddField(
            model_name='classinstanceannouncement',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='class_announcements', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='class_instances', to='college.department'),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances',
                                    to='college.class'),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='regent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='ruled_classes', to='college.teacher'),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='students',
            field=models.ManyToManyField(through='college.Enrollment', to='college.Student'),
        ),
        migrations.AddField(
            model_name='classfile',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='files',
                                    to='college.classinstance'),
        ),
        migrations.AddField(
            model_name='classfile',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='class_files',
                                    to='college.file'),
        ),
        migrations.AddField(
            model_name='classfile',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.classfile'),
        ),
        migrations.AddField(
            model_name='classfile',
            name='uploader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='class_files', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classfile',
            name='uploader_teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='class_files', to='college.teacher'),
        ),
        migrations.AddField(
            model_name='class',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='classes',
                                    to='college.department'),
        ),
        migrations.AddField(
            model_name='class',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.class'),
        ),
        migrations.AddField(
            model_name='building',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.building'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='teachers', to='college.room'),
        ),
        migrations.AddField(
            model_name='shiftinstance',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='shift_instances', to='college.room'),
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together={('class_instance', 'shift_type', 'number')},
        ),
        migrations.AddField(
            model_name='room',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='rooms', to='college.department'),
        ),
        migrations.AddField(
            model_name='room',
            name='same_as',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='college.room'),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'class_instance')},
        ),
        migrations.AlterUniqueTogether(
            name='curriculum',
            unique_together={('course', 'corresponding_class')},
        ),
        migrations.AlterUniqueTogether(
            name='classinstance',
            unique_together={('parent', 'period', 'year')},
        ),
    ]
