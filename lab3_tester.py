from typing import List
from questions import Question, TextQuestion, ChoiceQuestion, RatingQuestion, MatchingQuestion, MultipleChoiceQuestion

# -------------------------- BASE TEST --------------------------

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
            print("  Немає питань.")
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
        found = [q for q in self.questions if keyword in q.text.lower()]
        return found


# -------------------------- INHERITANCE --------------------------

class BasicTest(Test):
    """Звичайний тест"""
    pass


class AdaptiveTest(Test):
    """Поліморфне додавання запитань"""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.current_difficulty = 1

    def add_question(self, question: Question):
        super().add_question(question)
        if question.difficulty > self.current_difficulty:
            self.current_difficulty = question.difficulty
            print(f"Новий рівень складності тесту: {self.current_difficulty}")


# -------------------------- TEST EDITOR --------------------------

class TestEditor:
    def __init__(self):
        self.tests: List[Test] = []

    def create_basic(self, name: str, description="") -> BasicTest:
        t = BasicTest(name, description)
        self.tests.append(t)
        return t

    def create_adaptive(self, name: str, description="") -> AdaptiveTest:
        t = AdaptiveTest(name, description)
        self.tests.append(t)
        return t

    def delete_test(self, index: int):
        if 0 <= index < len(self.tests):
            self.tests.pop(index)
        else:
            print("Невірний номер тесту.")

    def show_tests(self):
        print("\nУсі тести:")
        if not self.tests:
            print("  Немає тестів.")
            return
        for i, t in enumerate(self.tests, start=1):
            print(f"{i}. {t.name} — {len(t.questions)} питань")

    def find_test(self, name: str):
        name = name.lower()
        for t in self.tests:
            if t.name.lower() == name:
                return t
        return None
