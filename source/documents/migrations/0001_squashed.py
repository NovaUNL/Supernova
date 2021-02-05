from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('documents', '0001_initial')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('content', models.TextField()),
                ('creation', models.DateField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('last_edition', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ['creation'],
            },
        ),
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.document')),
            ],
        ),
    ]
