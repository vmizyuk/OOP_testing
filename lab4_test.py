import time
import random


# -------------------------- QUESTION FROM L2 --------------------------
class Question:
    def __init__(self, text, options=None, correct=None, difficulty=1):
        self.text = text
        self.options = options or []
        self.correct = correct
        self.difficulty = difficulty

    def show(self):
        print(self.text)
        for i, opt in enumerate(self.options, 1):
            print(f"{i}) {opt}")

    def check(self, answer):
        try:
            return self.options[int(answer) - 1].lower() == self.correct.lower()
        except:
            return False


# -------------------------- BASE SESSION --------------------------
class BaseSession:
    def __init__(self, questions):
        self.questions = questions

    def ask_question(self, q):  # поліморфний метод
        q.show()
        ans = input("Ваша відповідь: ")
        return q.check(ans)

    def start(self):
        score = 0
        for q in self.questions:
            if self.ask_question(q):
                score += 1
        print(f"Результат: {score}/{len(self.questions)}")


# -------------------------- TIMED SESSION --------------------------
class TimedSession(BaseSession):
    def ask_question(self, q):
        start = time.time()
        correct = super().ask_question(q)
        end = time.time()
        print(f"Час відповіді: {end - start:.2f} сек")
        return correct


# -------------------------- ADAPTIVE SESSION --------------------------
class AdaptiveSession(BaseSession):
    def start(self):
        score = 0
        difficulty = 1
        for _ in range(5):
            available = [q for q in self.questions if q.difficulty == difficulty]
            if not available:
                available = self.questions
            q = random.choice(available)

            if self.ask_question(q):
                score += 1
                difficulty = min(3, difficulty + 1)
            else:
                difficulty = max(1, difficulty - 1)

        print(f"Ваш бал: {score}/5")


# ======================================================
#         PATTERN: FACTORY METHOD (Фабрика)
# ======================================================

class SessionFactory:
    """Створює потрібний тип сесії за запитом."""

    def create_session(self, session_type, questions):
        if session_type == "basic":
            return BaseSession(questions)
        elif session_type == "timed":
            return TimedSession(questions)
        elif session_type == "adaptive":
            return AdaptiveSession(questions)
        else:
            raise ValueError("Невідомий тип сесії")


# ======================================================
#         ПРИКЛАД ВИКЛИКУ
# ======================================================

if __name__ == "__main__":
    questions = [
        Question("Столиця Франції?", ["Париж", "Лондон", "Берлін"], "Париж", difficulty=1),
        Question("2 + 2 = ?", ["3", "4", "5"], "4", difficulty=1),
        Question("Найбільший океан?", ["Тихий", "Атлантичний", "Індійський"], "Тихий", difficulty=2),
    ]

    factory = SessionFactory()

    # створення timed сесії через фабрику
    session = factory.create_session("timed", questions)

    session.start()
