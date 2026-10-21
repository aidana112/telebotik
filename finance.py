# ЛР 4: модуль с формулами, в bot.py формул нет

# сценарии цены сырья через год
UP = 1.3
DOWN = 0.7
PROBABILITY = 0.5
# дольше этого срока окупаемость не ищем
MAX_YEARS = 100

# ЛР 3: словарь проектов, параметры каждого проекта в кортеже
# (инвестиции, потоки в разные годы цикла цен, ставка, срок)
# цифры условные
PROJECTS = {
    "Медный рудник": (1000, (180, 220, 200), 0.12, 10),
    "Золотое месторождение": (1500, (260, 300, 280), 0.14, 12),
    "Урановый рудник": (2000, (300, 380, 340), 0.15, 15),
}

# подписи к ключам отчёта
LABELS = {"npv": "NPV", "payback": "Окупаемость"}


def discount_factors(rate, years):
    # ЛР 3: генератор списка, коэффициенты дисконтирования
    return [1 / (1 + rate) ** t for t in range(1, years + 1)]


def npv(investment, cash_flow, rate, years):
    total = -investment
    # ЛР 2: цикл for, арифметика и оператор присваивания +=
    for factor in discount_factors(rate, years):
        total += cash_flow * factor
    return total


def payback(investment, cash_flow):
    total = 0
    years = 0
    # ЛР 2: цикл while, прибавляем поток по одному году
    while total < investment and years < MAX_YEARS:
        total += cash_flow
        years += 1
    if total < investment:
        return None
    return years


# ЛР 4: функция с *args, средний поток по годам цикла цен
def average_flow(*flows):
    if len(flows) == 0:
        return 0
    return sum(flows) / len(flows)


# ЛР 4: функция с **kwargs, собирает отчёт из именованных параметров
def make_report(**params):
    lines = []
    for key, value in params.items():
        lines.append(f"{LABELS.get(key, key)}: {value}")
    return "\n".join(lines)


# срок со словом: 1 год, 3 года, 5 лет
def years_text(years):
    if years is None:
        return f"больше {MAX_YEARS} лет"
    if years % 10 == 1 and years % 100 != 11:
        word = "год"
    elif years % 10 in (2, 3, 4) and years % 100 not in (12, 13, 14):
        word = "года"
    else:
        word = "лет"
    return f"{years} {word}"


def verdict(value):
    # ЛР 2: if/else, вывод о проекте
    if value > 0:
        return "Проект выгоден."
    else:
        return "Проект невыгоден."


# ЛР 5.2: класс, __init__, self, методы
class Project:
    def __init__(self, name, investment, cash_flow, rate, years):
        self.name = name
        self.investment = investment
        # ЛР 5.2: инкапсуляция, поток читаем только через get_cash_flow()
        self._cash_flow = cash_flow
        self.rate = rate
        self.years = int(years)

    def get_cash_flow(self):
        return self._cash_flow

    def npv(self):
        return npv(self.investment, self.get_cash_flow(), self.rate, self.years)

    def payback(self):
        return payback(self.investment, self.get_cash_flow())

    # ценность проекта, если запустить его сейчас
    def value(self):
        return self.npv()


# ЛР 5.2: наследование, DelayedProject получает все методы Project
class DelayedProject(Project):
    def scenario_npv(self, factor):
        return npv(self.investment, self.get_cash_flow() * factor, self.rate, self.years)

    # ЛР 5.2: полиморфизм, value() переопределён под вариант «подождать год»
    def value(self):
        npv_up = self.scenario_npv(UP)
        npv_down = self.scenario_npv(DOWN)
        # если NPV отрицательный, проект не запускают, поэтому берём 0
        if npv_up < 0:
            npv_up = 0
        if npv_down < 0:
            npv_down = 0
        expected = PROBABILITY * npv_up + PROBABILITY * npv_down
        return expected / (1 + self.rate)


def project_report(project):
    value = project.npv()
    report = make_report(npv=round(value, 2), payback=years_text(project.payback()))
    return report + "\n" + verdict(value)


def payback_text(investment, cash_flow):
    return make_report(payback=years_text(payback(investment, cash_flow)))


def delay_advice(now_value, wait_value):
    flexibility = wait_value - now_value
    text = f"Ценность гибкости: {round(flexibility, 2)}\n"
    # ЛР 2: if/elif/else
    if flexibility > 0:
        return text + "Выгоднее подождать год."
    elif flexibility < 0:
        return text + "Выгоднее запустить сейчас."
    else:
        return text + "Варианты равны."


def ranked_projects():
    # ЛР 3: результаты собираем в список
    results = []
    for name, params in PROJECTS.items():
        investment, flows, rate, years = params
        project = Project(name, investment, average_flow(*flows), rate, years)
        results.append((name, project.npv()))
    # ЛР 4: lambda как ключ сортировки, минус ставит больший NPV первым
    results.sort(key=lambda item: -item[1])
    return results


def projects_text():
    lines = ["Учебные проекты:", ""]
    # ЛР 3: вложенный цикл, внешний идёт по проектам, внутренний по их потокам
    for name, value in ranked_projects():
        flows = []
        for flow in PROJECTS[name][1]:
            flows.append(f"{flow}")
        lines.append(f"{name}: NPV {round(value, 2)}, потоки {', '.join(flows)}")
    return "\n".join(lines)


if __name__ == "__main__":
    # контрольный пример из CLAUDE.md: I=1000, CF=200, r=0.12, T=10
    now = Project("Запустить сейчас", 1000, 200, 0.12, 10)
    wait = DelayedProject("Подождать год", 1000, 200, 0.12, 10)
    print("NPV сейчас:", round(now.npv(), 2))
    print("NPV_up:", round(wait.scenario_npv(UP), 2))
    print("NPV_down:", round(wait.scenario_npv(DOWN), 2))
    print("Стоимость ожидания:", round(wait.value(), 2))
    print(delay_advice(now.value(), wait.value()))
    print("Срок окупаемости:", now.payback())
    print(projects_text())
