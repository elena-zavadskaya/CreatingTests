# Generated by Django 4.2.18 on 2025-01-29 01:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0006_alter_answer_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('is_correct', models.BooleanField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='teachers.question')),
                ('selected_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='teachers.answer')),
            ],
            options={
                'verbose_name': 'Ответ студента',
                'verbose_name_plural': 'Ответы студентов',
            },
        ),
    ]
