# Generated by Django 4.2 on 2023-04-29 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='difficulty',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
