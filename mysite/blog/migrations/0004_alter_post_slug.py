# Generated by Django 4.1.2 on 2024-10-18 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_post_options_rename_user_post_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=250, unique_for_date='publish', verbose_name='Slug'),
        ),
    ]
