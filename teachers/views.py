from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import Test, StudentResult, Teacher, Question, Answer


def create_test(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        test_name = request.POST.get('test-name')
        questions = []

        # Собираем данные о вопросах и ответах
        for key, value in request.POST.items():
            if key.startswith('question-text-'):
                question_id = key.split('-')[-1]
                question_text = value
                answers = []

                # Собираем варианты ответов для текущего вопроса
                for i in range(1, 5):
                    answer_text = request.POST.get(f'answer-{question_id}-{i}')
                    is_correct = request.POST.get(f'correct-answer-{question_id}') == str(i)
                    if answer_text:
                        answers.append({
                            'text': answer_text,
                            'is_correct': is_correct
                        })

                questions.append({
                    'text': question_text,
                    'answers': answers
                })

        # Проверка данных
        if not test_name:
            messages.error(request, 'Название теста обязательно.')
        elif not questions:
            messages.error(request, 'Добавьте хотя бы один вопрос.')
        else:
            # Проверка, что все вопросы имеют 4 ответа и один правильный
            valid = True
            for question in questions:
                if len(question['answers']) != 4:
                    valid = False
                    messages.error(request, 'Каждый вопрос должен иметь 4 варианта ответа.')
                    break
                if not any(answer['is_correct'] for answer in question['answers']):
                    valid = False
                    messages.error(request, 'Для каждого вопроса выберите правильный ответ.')
                    break

            if valid:
                try:
                    with transaction.atomic():  # Используем транзакцию для целостности данных
                        # Получаем текущего преподавателя
                        teacher = Teacher.objects.get(user=request.user)

                        # Создаем тест
                        test = Test(name=test_name, teacher=teacher)
                        test.save()

                        # Создаем вопросы и ответы
                        for question_data in questions:
                            question = Question(test=test, question_text=question_data['text'])
                            question.save()

                            for answer_data in question_data['answers']:
                                answer = Answer(
                                    question=question,
                                    answer_text=answer_data['text'],
                                    is_correct=answer_data['is_correct']
                                )
                                answer.save()

                        # Обновляем количество вопросов в тесте
                        test.question_count = len(questions)
                        test.save()

                        messages.success(request, 'Тест успешно создан!')
                        return redirect('view_tests')
                except Exception as e:
                    messages.error(request, f'Ошибка при создании теста: {str(e)}')

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
