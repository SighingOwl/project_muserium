# Generated by Django 5.0.7 on 2024-08-02 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0007_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carousel',
            name='background_color',
            field=models.CharField(default='#000000', max_length=50),
        ),
    ]
