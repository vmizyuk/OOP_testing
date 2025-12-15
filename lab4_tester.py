from typing import List, Optional
from questions import Question
from test import Test, BasicTest, AdaptiveTest


class TestBuilder:
    def __init__(self):
        self._test: Optional[Test] = None

    def create_basic_test(self, name: str, description: str = "") -> "TestBuilder":
        self._test = BasicTest(name, description)
        return self

    def create_adaptive_test(self, name: str, description: str = "") -> "TestBuilder":
        self._test = AdaptiveTest(name, description)
        return self

    def add_question(self, question: Question) -> "TestBuilder":
        if self._test is None:
            raise RuntimeError("Спочатку створіть тест")
        self._test.add_question(question)
        return self

    def build(self) -> Test:
        if self._test is None:
            raise RuntimeError("Тест не створено")
        result = self._test
        self._test = None
        return result


class TestEditor:
    def __init__(self):
        self.tests: List[Test] = []
        self.builder = TestBuilder()

    def add_test(self, test: Test) -> None:
        self.tests.append(test)

    def create_basic(self, name: str, description: str = "") -> BasicTest:
        test = BasicTest(name, description)
        self.tests.append(test)
        return test

    def create_adaptive(self, name: str, description: str = "") -> AdaptiveTest:
        test = AdaptiveTest(name, description)
        self.tests.append(test)
        return test

    def delete_test(self, index: int) -> None:
        if 0 <= index < len(self.tests):
            self.tests.pop(index)
        else:
            print("Невірний номер тесту")

    def show_tests(self) -> None:
        print("\nУсі тести:")
        if not self.tests:
            print("  Немає тестів.")
            return
        for i, t in enumerate(self.tests, start=1):
            print(f"{i}. {t.name} — {len(t.questions)} питань")

    def find_test(self, name: str) -> Optional[Test]:
        name = name.lower()
        for t in self.tests:
            if t.name.lower() == name:
                return t
        return None

    # ===== Google Forms style editing =====

    def add_question_to_test(self, test: Test, question: Question) -> None:
        test.add_question(question)

    def remove_question_from_test(self, test: Test, index: int) -> None:
        test.remove_question(index)

    def edit_question_text(self, test: Test, index: int, new_text: str) -> None:
        if 0 <= index < len(test.questions):
            test.questions[index].text = new_text
        else:
            print("Невірний індекс питання")

    def edit_question_topic(self, test: Test, index: int, new_topic: str) -> None:
        if 0 <= index < len(test.questions):
            test.questions[index].topic = new_topic
        else:
            print("Невірний індекс питання")

    def edit_question_difficulty(self, test: Test, index: int, new_difficulty: int) -> None:
        if 0 <= index < len(test.questions):
            test.questions[index].difficulty = new_difficulty
        else:
            print("Невірний індекс питання")

    def search_questions(self, test: Test, keyword: str) -> List[Question]:
        return test.find_questions(keyword)

    def global_search(self, keyword: str) -> List[Question]:
        result = []
        for t in self.tests:
            result.extend(t.find_questions(keyword))
        return result
