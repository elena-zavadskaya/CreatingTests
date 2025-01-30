from django.contrib.auth.models import User
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
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('view_tests')
        else:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        password = request.POST['password']

        # Создаем пользователя
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Создаем преподавателя или студента (в зависимости от вашей логики)
        teacher = Teacher(full_name=full_name, password=password)
        teacher.save()

        # Авторизуем пользователя
        login(request, user)
        return redirect('view_tests')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')
