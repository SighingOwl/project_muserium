# Generated by Django 5.0.8 on 2024-08-17 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_review_content_rating_review_readiness_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qna',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
