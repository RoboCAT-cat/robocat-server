# Generated by Django 3.0.2 on 2020-01-17 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='black_adhoc',
            field=models.IntegerField(default=0, verbose_name='ad-hoc points for black team'),
        ),
        migrations.AddField(
            model_name='score',
            name='notes',
            field=models.TextField(blank=True, default='', verbose_name='notes'),
        ),
        migrations.AddField(
            model_name='score',
            name='white_adhoc',
            field=models.IntegerField(default=0, verbose_name='ad-hoc points for white team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='partial_black_score',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='match_as_partial_black', to='matches.Score', verbose_name='partial score for black team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='partial_white_score',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='match_as_partial_white', to='matches.Score', verbose_name='partial score for white team'),
        ),
    ]
