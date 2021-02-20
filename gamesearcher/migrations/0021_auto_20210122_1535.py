# Generated by Django 3.1.2 on 2021-01-22 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamesearcher', '0020_auto_20210122_1242'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indiegame',
            old_name='publishDate',
            new_name='lastVersionDate',
        ),
        migrations.AlterField(
            model_name='indiegame',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='mainstreamgame',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
