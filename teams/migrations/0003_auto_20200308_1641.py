# Generated by Django 3.0.3 on 2020-03-08 16:41

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_team_raffle'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='team',
            managers=[
                ('ranked_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
