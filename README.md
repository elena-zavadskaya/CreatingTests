# Проект для создания тестов

## Установка

1. **Склонируйте репозиторий:**
   ```bash
   git clone https://github.com/ваш-репозиторий.git
   ```
2. **Перейдите в директорию проекта:**

   ```bash
   cd ваш-проект
   ```
3. **Создайте виртуальное окружение:**

   ```bash
   python -m venv venv
   ```
4. **Активируйте виртуальное окружение:**

   - **На Windows:**

   ```bash
   venv\Scripts\activate
   ```
   - **На macOS/Linux:**
  
   ```bash
   source venv/bin/activate
   ```
5. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```
6. **Настройте базу данных:**

   - **Создайте базу данных MySQL.**
  
   - **Обновите настройки в settings.py:**

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'ваша_база_данных',
           'USER': 'ваш_пользователь',
           'PASSWORD': 'ваш_пароль',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
7. **Примените миграции:**

   ```bash
   python manage.py migrate
   ```
8. **Запустите сервер:**

   ```bash
   python manage.py runserver
   ```
## Использование
Откройте браузер и перейдите по адресу http://127.0.0.1:8000/.
