import re

# ЛР 4: регулярное выражение, число без знака: 1000 или 0.12
NUMBER_PATTERN = r"^\d{1,9}(\.\d{1,6})?$"


# достаёт count чисел из текста команды, при неверном вводе возвращает None
def parse_numbers(text, count):
    # первое слово это сама команда, например /npv
    words = text.split()[1:]
    if len(words) != count:
        return None
    numbers = []
    for word in words:
        word = word.replace(",", ".")
        # ЛР 4: try/except, буквы вместо числа не роняют бота
        try:
            number = float(word)
        except ValueError:
            return None
        # float() пропускает -200, 1e5 и nan, регулярное выражение их отсекает
        if re.match(NUMBER_PATTERN, word) is None:
            return None
        numbers.append(number)
    return numbers


# проверяет смысл параметров проекта, возвращает текст ошибки или None
def check_project(numbers):
    if numbers is None:
        return "Нужно 4 числа: инвестиции, поток за год, ставка, срок."
    investment, cash_flow, rate, years = numbers
    # ЛР 2: логические операторы and, or, not
    if investment == 0 or cash_flow == 0:
        return "Инвестиции и поток должны быть больше 0."
    if rate > 1:
        return "Ставку пишите дробью, 12% это 0.12."
    if not (years >= 1 and years <= 50 and years == int(years)):
        return "Срок пишите целым числом от 1 до 50."
    return None
