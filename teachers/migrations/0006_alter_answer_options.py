# Generated by Django 4.2.18 on 2025-01-29 00:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0005_answer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
    ]
