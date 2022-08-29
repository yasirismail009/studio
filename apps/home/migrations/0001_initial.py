# Generated by Django 3.2.6 on 2021-12-16 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SlidesData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('major', models.CharField(max_length=250)),
                ('school', models.CharField(max_length=250)),
                ('honor', models.CharField(max_length=250)),
                ('image', models.CharField(default='', max_length=250)),
                ('audio', models.CharField(default='', max_length=250)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=2)),
            ],
        ),
    ]
