# Generated by Django 5.0.8 on 2024-08-20 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_rename_qna_question_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
