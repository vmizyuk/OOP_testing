from abc import ABC, abstractmethod
from typing import List, Dict
import time

class Question(ABC):
    def __init__(self, text: str, correct_answer=None, topic: str = "", difficulty: int = 1):
        self.text = text
        self.correct_answer = correct_answer
        self.topic = topic
        self.difficulty = difficulty

    @abstractmethod
    def show_question(self):
        pass

    @abstractmethod
    def check_answer(self, user_answer):
        pass

class TextQuestion(Question):
    def __init__(
        self,
        text: str,
        correct_answer: str,
        topic: str = "",
        difficulty: int = 1,
        partial_allowed: bool = True
    ):
        super().__init__(text, correct_answer, topic, difficulty)
        self.partial_allowed = partial_allowed

    def show_question(self):
        print(self.text)

    def check_answer(self, user_answer):
        user_answer = user_answer.strip().lower()
        correct = str(self.correct_answer).lower()

        if user_answer == correct:
            return True
        if self.partial_allowed and user_answer in correct:
            return True
        return False
class Test:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.questions: List[Question] = []

    def add_question(self, question: Question):
        self.questions.append(question)

    def show_all_questions(self):
        print(f"\nПитання тесту '{self.name}':")
        if not self.questions:
            print("Немає питань.")
            return
        for i, q in enumerate(self.questions, start=1):
            print(f"{i}. {q.text}")

    def remove_question(self, index: int):
        if 0 <= index < len(self.questions):
            self.questions.pop(index)
        else:
            print("Невірний індекс питання.")

    def find_questions(self, keyword: str):
        keyword = keyword.lower()
        return [q for q in self.questions if keyword in q.text.lower()]

class BasicTest(Test):
    """Звичайний тест"""
    pass

class AdaptiveTest(Test):
    """Адаптивний тест"""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.current_difficulty = 1

    def add_question(self, question: Question):
        super().add_question(question)
        if question.difficulty > self.current_difficulty:
            self.current_difficulty = question.difficulty

class TestEditor:
    def __init__(self):
        self.tests: List[Test] = []

    def create_basic(self, name: str, description: str = "") -> BasicTest:
        test = BasicTest(name, description)
        self.tests.append(test)
        return test

    def create_adaptive(self, name: str, description: str = "") -> AdaptiveTest:
        test = AdaptiveTest(name, description)
        self.tests.append(test)
        return test

    def delete_test(self, index: int):
        if 0 <= index < len(self.tests):
            self.tests.pop(index)
        else:
            print("Невірний номер тесту.")

    def show_tests(self):
        if not self.tests:
            print("Немає тестів.")
            return
        for i, t in enumerate(self.tests, start=1):
            print(f"{i}. {t.name} — {len(t.questions)} питань")

    def find_test(self, name: str):
        for t in self.tests:
            if t.name.lower() == name.lower():
                return t
        return None

class TestSession:
    """
    Третя лабораторна робота.
    Проходження тесту користувачем.
    """

    def __init__(self, test: Test):
        self.test = test
        self.score = 0
        self.answers: Dict[int, bool] = {}
        self.total_time = 0.0

    def start(self):
        if not self.test.questions:
            print("Тест не містить питань.")
            return

        print(f"\nПОЧАТОК ТЕСТУ: {self.test.name}")
        if self.test.description:
            print(self.test.description)

        start_time = time.time()

        for index, question in enumerate(self.test.questions, start=1):
            print(f"\nПитання {index}/{len(self.test.questions)}")
            question.show_question()
            user_answer = input("Ваша відповідь: ")

            correct = question.check_answer(user_answer)
            self.answers[index] = correct

            if correct:
                print("Правильно")
                self.score += 1
            else:
                print("Неправильно")

        self.total_time = time.time() - start_time
        self.show_result()

    def show_result(self):
        print("\nРЕЗУЛЬТАТИ ТЕСТУ")
        print(f"Правильних відповідей: {self.score}/{len(self.test.questions)}")
        print(f"Час проходження: {self.total_time:.2f} сек")


