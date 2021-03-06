# Generated by Django 3.0.1 on 2020-01-05 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=128)),
                ('real_name', models.CharField(max_length=32)),
                ('current_path', models.CharField(max_length=2048)),
                ('upload_time', models.DateTimeField()),
                ('if_delete', models.BooleanField()),
                ('if_dir', models.BooleanField()),
                ('file_size', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('select_id', models.IntegerField(primary_key=True, serialize=False)),
                ('display_name', models.CharField(max_length=64)),
                ('ext_name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField()),
                ('token', models.CharField(max_length=64)),
                ('valid_period', models.IntegerField()),
                ('target_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_file', to='management.File')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_belong', to='user.User')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=128)),
                ('content', models.TextField(max_length=1024)),
                ('create_time', models.DateTimeField()),
                ('target_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_link', to='management.ShareLink')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='management.FileType'),
        ),
        migrations.AddField(
            model_name='file',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User'),
        ),
    ]
