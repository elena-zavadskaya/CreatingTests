import logging
import django
import os
import random
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from django.utils.timezone import now
from asgiref.sync import sync_to_async


# Указываем путь к Django-приложению
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CreatingTests.settings")
django.setup()


from teachers.models import Student, Test, Question, Answer, StudentAnswer, StudentResult


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


TOKEN = "7887883202:AAFs9MB5EAiJUocNA9ZwudT---rNyamdFlw"


# ==============================
# БАЗОВЫЕ ФУНКЦИИ ДЛЯ БД
# ==============================


@sync_to_async
def get_or_create_student(nickname, full_name=None):
   """Получает или создает запись о студенте."""
   student, created = Student.objects.get_or_create(nickname=nickname)
   if full_name and created:
       student.full_name = full_name
       student.save()
   return student, created


@sync_to_async
def update_student_full_name(nickname, full_name):
   """Обновляет ФИО студента после ввода."""
   student = Student.objects.get(nickname=nickname)
   student.full_name = full_name
   student.save()


@sync_to_async
def get_tests():
   """Возвращает список всех тестов."""
   return list(Test.objects.all())


@sync_to_async
def get_test(test_id):
   """Возвращает тест по его ID."""
   return Test.objects.get(id=test_id)


@sync_to_async
def get_questions(test):
   """Возвращает список вопросов для теста в случайном порядке."""
   questions = list(test.questions.all())
   random.shuffle(questions)
   return questions


@sync_to_async
def get_answers(question):
   """Возвращает список ответов для вопроса в случайном порядке."""
   answers = list(question.answers.all())
   random.shuffle(answers)
   return answers


@sync_to_async
def get_student(nickname):
   """Получает запись о студенте по никнейму."""
   return Student.objects.get(nickname=nickname)


@sync_to_async
def get_answer(answer_id):
   """Получает ответ по его ID."""
   return Answer.objects.get(id=answer_id)


@sync_to_async
def get_question_from_answer(answer):
   """Возвращает вопрос, к которому принадлежит ответ."""
   return answer.question


@sync_to_async
def save_student_answer(question, answer, student):
   """Сохраняет ответ студента."""
   return StudentAnswer.objects.create(
       question=question,
       selected_answer=answer,
       is_correct=answer.is_correct,
       student=student
   )


@sync_to_async
def save_result(student, test, score):
   """Сохраняет результат текущей попытки прохождения теста."""
   return StudentResult.objects.create(
       student=student,
       test=test,
       correct_answers=score,
       total_questions=test.question_count,
       attempt_timestamp=now()
   )


# ==============================
# КОМАНДЫ И ФУНКЦИИ БОТА
# ==============================


async def start(update: Update, context: CallbackContext):
   """Обрабатывает команду /start, проверяет регистрацию и предлагает выбрать тест."""
   user = update.message.from_user
   student, created = await get_or_create_student(nickname=user.username)


   if created or not student.full_name:
       await update.message.reply_text(
           "Привет! Давайте зарегистрируемся. Введите ваше ФИО:"
       )
       context.user_data["waiting_for_full_name"] = True
       return


   await update.message.reply_text(
       f"С возвращением, {student.full_name}!",
       reply_markup=ReplyKeyboardRemove()
   )
   return await show_tests(update, context)




async def receive_full_name(update: Update, context: CallbackContext):
   """Обрабатывает ввод ФИО."""
   user = update.message.from_user
   full_name = update.message.text.strip()


   await update_student_full_name(user.username, full_name)
   await update.message.reply_text(
       f"Спасибо, {full_name}! Теперь вы зарегистрированы.",
       reply_markup=ReplyKeyboardRemove()
   )
   return await show_tests(update, context)


async def help_command(update: Update, context: CallbackContext):
   """Команда /help."""
   help_text = (
       "Этот бот помогает проходить тесты.\n\n"
       "Доступные команды:\n"
       "/start - Главное меню\n"
       "/test - Выбор теста\n"
       "/help - Информация о боте"
   )
   await update.message.reply_text(help_text)


async def show_tests(update: Update, context: CallbackContext):
   """Показывает список доступных тестов."""
   tests = await get_tests()
   keyboard = [[InlineKeyboardButton(test.name, callback_data=f'test_{test.id}')] for test in tests]
   reply_markup = InlineKeyboardMarkup(keyboard)
   await update.message.reply_text("Выберите тест:", reply_markup=reply_markup)


async def handle_test_selection(update: Update, context: CallbackContext):
   """Обрабатывает выбор теста."""
   query = update.callback_query
   await query.answer()
   test_id = int(query.data.split('_')[1])


   user = query.from_user
   student = await get_student(user.username)
   test = await get_test(test_id)


   context.user_data["test_id"] = test_id
   context.user_data["score"] = 0
   context.user_data["question_index"] = 0
   context.user_data["questions"] = await get_questions(test)


   return await ask_question(update, context)


async def ask_question(update: Update, context: CallbackContext):
   """Отправляет следующий вопрос пользователю."""
   query = update.callback_query
   questions = context.user_data["questions"]


   if context.user_data["question_index"] >= len(questions):
       return await finish_test(update, context)


   question = questions[context.user_data["question_index"]]
   context.user_data["current_question_id"] = question.id


   keyboard = [[InlineKeyboardButton(answer.answer_text, callback_data=f'answer_{answer.id}')] for answer in
               await get_answers(question)]
   reply_markup = InlineKeyboardMarkup(keyboard)


   await query.message.reply_text(text=question.question_text, reply_markup=reply_markup)


async def handle_answer(update: Update, context: CallbackContext):
   """Обрабатывает выбор ответа."""
   query = update.callback_query
   await query.answer()


   user = query.from_user
   student = await get_student(user.username)
   answer = await get_answer(int(query.data.split("_")[1]))
   question = await get_question_from_answer(answer)


   await save_student_answer(question, answer, student)


   if answer.is_correct:
       context.user_data["score"] += 1


   context.user_data["question_index"] += 1
   return await ask_question(update, context)


async def finish_test(update: Update, context: CallbackContext):
   """Завершает тест и сохраняет результат."""
   query = update.callback_query
   user = query.from_user
   student = await get_student(user.username)
   test = await get_test(context.user_data["test_id"])


   score = context.user_data.get("score", 0)
   await save_result(student, test, score)


   await query.message.reply_text(f"Тест завершен! Ваш результат: {score} из {len(context.user_data['questions'])}.")


def main():
   application = Application.builder().token(TOKEN).build()
   application.add_handler(CommandHandler("start", start))
   application.add_handler(CommandHandler("help", help_command))
   application.add_handler(CommandHandler("test", show_tests))
   application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_full_name))
   application.add_handler(CallbackQueryHandler(handle_test_selection, pattern="^test_"))
   application.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
   application.run_polling()


if __name__ == "__main__":
   main()