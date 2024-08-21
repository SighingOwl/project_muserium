# Generated by Django 5.0.8 on 2024-08-21 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glass_class', '0004_reservation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='glassclass',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='glassclass',
            name='interests',
        ),
        migrations.AddField(
            model_name='glassclass',
            name='average_rating',
            field=models.FloatField(default=0),
        ),
    ]
