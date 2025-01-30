from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import Test, StudentResult, Teacher


def create_test(request):
    if request.method == 'POST':
        # Обработка создания теста
        pass
    return render(request, 'create_test.html')

def view_tests(request):
    tests = Test.objects.all()
    return render(request, 'view_tests.html', {'tests': tests})

def view_results(request):
    results = StudentResult.objects.all()
    return render(request, 'view_results.html', {'results': results})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Сначала проверяем аутентификацию через Django User
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('view_tests')

        # Если пользователь не найден, проверяем в модели Teacher
        try:
            teacher = Teacher.objects.get(nickname=username)
            if teacher.check_password(password):  # Проверяем пароль
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('view_tests')
            else:
                return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})
        except Teacher.DoesNotExist:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})

    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        password = request.POST['password']

        # Проверяем, существует ли уже пользователь с таким ником
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Никнейм уже используется'})

        try:
            with transaction.atomic():  # Оборачиваем в транзакцию, чтобы избежать ошибок
                # Создаем пользователя Django (для аутентификации)
                user = User.objects.create_user(username=username, password=password)

                # Создаем преподавателя и связываем с пользователем
                teacher = Teacher(full_name=full_name, nickname=username, user=user)
                teacher.set_password(password)  # Хэшируем пароль
                teacher.save()

                # Авторизуем пользователя
                login(request, user)
                return redirect('view_tests')
        except Exception as e:
            return render(request, 'register.html', {'error': f'Ошибка регистрации: {str(e)}'})

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')
