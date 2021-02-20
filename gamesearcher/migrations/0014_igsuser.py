# Generated by Django 3.1.2 on 2021-01-04 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gamesearcher', '0013_auto_20210104_1914'),
    ]

    operations = [
        migrations.CreateModel(
            name='IGSUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indiegamesLiked', models.ManyToManyField(to='gamesearcher.IndieGame')),
                ('mainstreamgamesLiked', models.ManyToManyField(to='gamesearcher.MainstreamGame')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
