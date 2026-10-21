import os
import time

HISTORY_FILE = "data/history.txt"
LOG_FILE = "logs/bot.log"


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ЛР 5.1: запись в файл в режиме "a" через with
def save_history(user_id, text):
    os.makedirs("data", exist_ok=True)
    # одна запись это одна строка файла
    text = text.replace("\n", " | ")
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(f"{user_id};{now_text()} | {text}\n")


# ЛР 3: генератор с yield, отдаёт строки истории по одной
def read_history(user_id):
    if not os.path.exists(HISTORY_FILE):
        return
    prefix = f"{user_id};"
    with open(HISTORY_FILE, encoding="utf-8") as file:
        for line in file:
            if line.startswith(prefix):
                yield line.strip()[len(prefix):]


def last_history(user_id, n):
    lines = []
    # строки из генератора забираем циклом for
    for line in read_history(user_id):
        lines.append(line)
    return lines[-n:]


# ЛР 5.1: журнал ведём вручную, строка: дата;пользователь;команда;статус
def write_log(text):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{now_text()};{text}\n")


def last_log_lines(n):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, encoding="utf-8") as file:
        lines = file.readlines()
    return lines[-n:]
