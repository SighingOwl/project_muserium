# Generated by Django 5.0.8 on 2024-08-25 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('image_url', models.URLField()),
                ('alt', models.CharField(max_length=100)),
                ('url', models.URLField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Carousel Title', max_length=50)),
                ('image_url', models.URLField()),
                ('background_color', models.CharField(default='#000000', max_length=50)),
                ('alt', models.CharField(max_length=100)),
            ],
        ),
    ]
