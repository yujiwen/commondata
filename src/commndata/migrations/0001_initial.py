# Generated by Django 3.2 on 2021-04-29 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CodeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('created_at', models.DateTimeField(serialize=False, verbose_name='created_at')),
                ('creator', models.CharField(max_length=120, serialize=False, verbose_name='creator')),
                ('updated_at', models.DateTimeField(serialize=False, verbose_name='updated_at')),
                ('updater', models.CharField(max_length=120, serialize=False, verbose_name='updater')),
                ('delete_flag', models.BooleanField(default=False, verbose_name='delete flag')),
                ('codecategory', models.CharField(max_length=32, verbose_name='code category')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('display_order', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'code category',
                'verbose_name_plural': 'code category',
                'ordering': ['display_order'],
                'permissions': [('import_codecategory', 'Can import Code Category'), ('export_codecategory', 'Can export Code Category')],
            },
        ),
        migrations.CreateModel(
            name='CodeMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('created_at', models.DateTimeField(serialize=False, verbose_name='created_at')),
                ('creator', models.CharField(max_length=120, serialize=False, verbose_name='creator')),
                ('updated_at', models.DateTimeField(serialize=False, verbose_name='updated_at')),
                ('updater', models.CharField(max_length=120, serialize=False, verbose_name='updater')),
                ('delete_flag', models.BooleanField(default=False, verbose_name='delete flag')),
                ('start_date', models.DateField(verbose_name='start_date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='end_date')),
                ('code', models.CharField(max_length=32, verbose_name='code')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('value', models.CharField(blank=True, max_length=128, verbose_name='value')),
                ('display_order', models.IntegerField(blank=True, null=True)),
                ('codecategory', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='commndata.codecategory', verbose_name='code category')),
            ],
            options={
                'verbose_name': 'code master',
                'verbose_name_plural': 'code master',
                'ordering': ['codecategory', 'display_order', 'code', '-start_date'],
                'permissions': [('import_codemaster', 'Can import Code Master'), ('export_codemaster', 'Can export Code Master')],
            },
        ),
        migrations.AddConstraint(
            model_name='codecategory',
            constraint=models.UniqueConstraint(fields=('codecategory',), name='codecategory_unique'),
        ),
        migrations.AddConstraint(
            model_name='codemaster',
            constraint=models.UniqueConstraint(fields=('start_date', 'codecategory', 'code'), name='codemaster_unique'),
        ),
    ]
