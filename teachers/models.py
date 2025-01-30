from django.db import models
from django.contrib.auth.hashers import make_password

class Teacher(models.Model):
    # Уникальный ID создается автоматически Django как первичный ключ
    id = models.BigAutoField(primary_key=True)

    # ФИО преподавателя
    full_name = models.CharField(
        max_length=100,
        verbose_name="ФИО",
        help_text="Введите полное имя преподавателя (Фамилия Имя Отчество)"
    )

    # Хэшированный пароль преподавателя
    password = models.CharField(
        max_length=255,
        verbose_name="Пароль"
    )

    # Метод для сохранения хэшированного пароля
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


class Student(models.Model):
    # Уникальный ID создается автоматически Django как первичный ключ
    id = models.BigAutoField(primary_key=True)

    # ФИО студента
    full_name = models.CharField(
        max_length=100,
        verbose_name="ФИО",
        help_text="Введите полное имя студента (Фамилия Имя Отчество)"
    )

    # Хэшированный пароль студента
    password = models.CharField(
        max_length=255,
        verbose_name="Пароль"
    )

    # Метод для сохранения хэшированного пароля
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"


class Test(models.Model):
    # Уникальный id, который автоматически генерируется
    id = models.BigAutoField(primary_key=True)

    # Название теста
    name = models.CharField(
        max_length=200,
        verbose_name="Название теста",
        help_text="Введите название теста"
    )

    # Количество вопросов, будет автоматически заполняться
    question_count = models.IntegerField(default=0)

    # Преподаватель, который создал этот тест (внешний ключ)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class Question(models.Model):
    # Уникальный id, который автоматически генерируется
    id = models.BigAutoField(primary_key=True)

    # Внешний ключ на тест
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")

    # Текст вопроса
    question_text = models.CharField(
        max_length=500,
        verbose_name="Содержание вопроса",
        help_text="Введите текст вопроса"
    )

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    # Уникальный id, который автоматически генерируется
    id = models.BigAutoField(primary_key=True)

    # Внешний ключ на вопрос
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")

    # Текст ответа
    answer_text = models.CharField(
        max_length=300,
        verbose_name="Текст ответа",
        help_text="Введите текст ответа"
    )

    # Поле для указания корректности ответа
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Корректность ответа",
        help_text="Выберите, является ли этот ответ правильным"
    )

    def __str__(self):
        return self.answer_text

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class StudentAnswer(models.Model):
    # Уникальный id, который автоматически генерируется
    id = models.BigAutoField(primary_key=True)

    # Внешний ключ на вопрос
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="student_answers")

    # Внешний ключ на выбранный ответ
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="student_answers")

    # Поле для проверки правильности ответа
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Ответ студента на {self.question} - {'Правильный' if self.is_correct else 'Неправильный'}"

    class Meta:
        verbose_name = "Ответ студента"
        verbose_name_plural = "Ответы студентов"


class StudentResult(models.Model):
    # Уникальный id результата
    id = models.BigAutoField(primary_key=True)

    # Внешний ключ на тест
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")

    # Внешний ключ на студента
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")

    # Количество правильных ответов
    correct_answers = models.IntegerField(default=0)

    # Общее количество вопросов в тесте (из таблицы Test)
    total_questions = models.IntegerField()

    def calculate_correct_answers(self):
        """Подсчет количества правильных ответов студента."""
        return StudentAnswer.objects.filter(
            question__test=self.test,
            selected_answer__is_correct=True,
            student=self.student
        ).count()

    def save(self, *args, **kwargs):
        """При сохранении результата автоматически рассчитываем правильные ответы."""
        self.correct_answers = self.calculate_correct_answers()
        self.total_questions = self.test.question_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Результат студента {self.student.full_name} в тесте {self.test.name}: {self.correct_answers} из {self.total_questions}"

    class Meta:
        verbose_name = "Результат студента"
        verbose_name_plural = "Результаты студентов"