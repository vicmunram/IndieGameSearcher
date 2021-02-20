# Generated by Django 3.1.2 on 2021-01-28 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamesearcher', '0027_igsuser_recommendedgames'),
    ]

    operations = [
        migrations.AddField(
            model_name='igsuser',
            name='dislikedIndieGames',
            field=models.ManyToManyField(blank=True, related_name='dislikedIndieGames', to='gamesearcher.IndieGame'),
        ),
    ]