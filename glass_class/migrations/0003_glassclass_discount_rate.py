# Generated by Django 5.0.8 on 2024-08-09 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glass_class', '0002_glassclass_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='glassclass',
            name='discount_rate',
            field=models.IntegerField(default=0),
        ),
    ]
