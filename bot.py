import os
import sys

import telebot

# ЛР 4: модули, формулы в finance.py, проверки в validators.py, файлы в storage.py
import finance
import storage
import validators

# токен лежит в config.py, этот файл не попадает в git
if not os.path.exists("config.py"):
    print("Скопируйте config.example.py в config.py и вставьте токен")
    sys.exit(1)

from config import TOKEN

if ":" not in TOKEN:
    print("Скопируйте config.example.py в config.py и вставьте токен")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ЛР 3: множество, каждый пользователь учитывается один раз
users = set()

HELP_TEXT = (
    "Считаю NPV проекта по добыче сырья.\n\n"
    "/npv 1000 200 0.12 10 считает NPV\n"
    "/payback 1000 200 считает срок окупаемости\n"
    "/delay 1000 200 0.12 10 сравнивает запуск сейчас и через год\n"
    "/projects показывает учебные проекты\n"
    "/history показывает ваши расчёты\n"
    "/log показывает журнал\n\n"
    "Порядок чисел: инвестиции, поток за год, ставка, срок."
)


def log_command(message, status):
    user_id = message.from_user.id
    users.add(user_id)
    command = message.text.split()[0]
    # обычный текст пользователя в журнал не пишем
    if not command.startswith("/"):
        command = "текст"
    storage.write_log(f"{user_id};{command};{status}")


def reply(message, text):
    log_command(message, "ok")
    bot.send_message(message.chat.id, text)


def send_answer(message, answer):
    storage.save_history(message.from_user.id, f"{message.text} | {answer}")
    reply(message, answer)


def send_hint(message, problem, example):
    log_command(message, "ошибка ввода")
    bot.send_message(message.chat.id, f"{problem}\nПример: {example}")


def read_project(message, example):
    numbers = validators.parse_numbers(message.text, 4)
    problem = validators.check_project(numbers)
    if problem is not None:
        send_hint(message, problem, example)
        return None
    return numbers


@bot.message_handler(commands=["start", "help"])
def send_help(message):
    users.add(message.from_user.id)
    reply(message, f"{HELP_TEXT}\n\nПользователей: {len(users)}")


@bot.message_handler(commands=["npv"])
def send_npv(message):
    numbers = read_project(message, "/npv 1000 200 0.12 10")
    if numbers is None:
        return
    project = finance.Project("Проект", *numbers)
    send_answer(message, finance.project_report(project))


@bot.message_handler(commands=["payback"])
def send_payback(message):
    numbers = validators.parse_numbers(message.text, 2)
    if numbers is None:
        send_hint(message, "Нужно 2 числа: инвестиции и поток за год.", "/payback 1000 200")
        return
    send_answer(message, finance.payback_text(numbers[0], numbers[1]))


@bot.message_handler(commands=["delay"])
def send_delay(message):
    numbers = read_project(message, "/delay 1000 200 0.12 10")
    if numbers is None:
        return
    now = finance.Project("Запустить сейчас", *numbers)
    wait = finance.DelayedProject("Подождать год", *numbers)
    lines = []
    # ЛР 5.2: полиморфизм, value() вызываем одинаково у обоих объектов
    for project in [now, wait]:
        lines.append(f"{project.name}: {round(project.value(), 2)}")
    lines.append(finance.delay_advice(now.value(), wait.value()))
    send_answer(message, "\n".join(lines))


@bot.message_handler(commands=["projects"])
def send_projects(message):
    reply(message, finance.projects_text())


@bot.message_handler(commands=["history"])
def send_history(message):
    lines = storage.last_history(message.from_user.id, 5)
    if len(lines) == 0:
        reply(message, "Расчётов пока нет.")
    else:
        reply(message, "Ваши расчёты:\n\n" + "\n\n".join(lines))


@bot.message_handler(commands=["log"])
def send_log(message):
    lines = storage.last_log_lines(10)
    if len(lines) == 0:
        reply(message, "Журнал пуст.")
    else:
        reply(message, "Журнал:\n" + "".join(lines))


# обычный текст и неизвестные команды, этот обработчик всегда после команд
@bot.message_handler(content_types=["text"])
def send_unknown(message):
    reply(message, "Не понимаю. Список команд: /help")


# запуск бота, всегда в конце файла
storage.write_log("system;start;ok")
print("Бот запущен. Чтобы остановить, нажмите Ctrl+C.")
bot.infinity_polling()
