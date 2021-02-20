# Generated by Django 3.1.2 on 2021-01-05 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamesearcher', '0016_auto_20210104_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='igsuser',
            name='recommendedGames',
        ),
        migrations.AddField(
            model_name='igsuser',
            name='platforms',
            field=models.ManyToManyField(to='gamesearcher.Platform'),
        ),
        migrations.AddField(
            model_name='mainstreamgame',
            name='platforms',
            field=models.ManyToManyField(to='gamesearcher.Platform'),
        ),
    ]
