from django.contrib import admin
from .models import Teacher, Student, Test, Question, Answer, StudentAnswer, StudentResult


# Регистрация модели Teacher
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name')
    search_fields = ('full_name',)

# Регистрация модели Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name')
    search_fields = ('full_name',)

# Регистрация модели Test
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'question_count')
    search_fields = ('name',)

# Регистрация модели Question
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'question_text')
    search_fields = ('question_text',)

# Регистрация модели Answer
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer_text', 'is_correct')
    search_fields = ('answer_text',)

# Регистрация модели StudentAnswer
@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'selected_answer', 'is_correct')
    search_fields = ('question__question_text',)

# Регистрация модели StudentResult
@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'test', 'correct_answers', 'total_questions')
    search_fields = ('student__full_name', 'test__name')