# Generated by Django 3.1.2 on 2021-05-10 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20210509_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='telescope',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='images/telescopes', verbose_name='Аватар'),
        ),
    ]