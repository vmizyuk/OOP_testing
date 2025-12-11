from typing import List, Optional
import random


class Question:
    def __init__(self, text: str, correct_answer: str, topic: str = "", difficulty: int = 1):
        self.text = text
        self.correct_answer = correct_answer
        self.topic = topic
        self.difficulty = difficulty

    def __str__(self) -> str:
        return f"[{self.topic or 'без теми'} | складність: {self.difficulty}] {self.text}"


class Test:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.questions: List[Question] = []

    def add_question(self, question: Question) -> None:
        self.questions.append(question)

    def create_and_add_question(self, text: str, correct_answer: str, topic: str = "", difficulty: int = 1) -> Question:
        q = Question(text=text, correct_answer=correct_answer, topic=topic, difficulty=difficulty)
        self.add_question(q)
        return q

    def show_all_questions(self) -> None:
        if not self.questions:
            print(f"У тесті '{self.name}' ще немає питань.")
            return
        print(f"\nПитання тесту '{self.name}':")
        for i, q in enumerate(self.questions, start=1):
            print(f"{i}. {q}")

    def edit_question_text(self, index: int, new_text: str) -> None:
        if 0 <= index < len(self.questions):
            self.questions[index].text = new_text
        else:
            print("Неправильний номер питання для редагування.")

    def change_correct_answer(self, index: int, new_answer: str) -> None:
        if 0 <= index < len(self.questions):
            self.questions[index].correct_answer = new_answer
        else:
            print("Неправильний номер питання для зміни відповіді.")

    def delete_question(self, index: int) -> None:
        if 0 <= index < len(self.questions):
            self.questions.pop(index)
        else:
            print("Неправильний номер питання для видалення.")

    def find_questions(self, keyword: str) -> List[Question]:
        found = [q for q in self.questions if keyword.lower() in q.text.lower()]
        return found

    def sort_questions_by_text(self) -> None:
        self.questions.sort(key=lambda q: q.text.lower())

    def sort_questions_by_difficulty(self) -> None:
        self.questions.sort(key=lambda q: q.difficulty)

    def shuffle_questions(self) -> None:
        random.shuffle(self.questions)

    def save_to_file(self, filename: str) -> None:
        if not self.questions:
            return
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Тест: {self.name}\nОпис: {self.description}\n\n")
            for i, q in enumerate(self.questions, start=1):
                f.write(f"{i}. {q.text}\n")


class TestEditor:
    def __init__(self):
        self.tests: List[Test] = []

    def create_test(self, name: str, description: str = "") -> Test:
        new_test = Test(name=name, description=description)
        self.tests.append(new_test)
        return new_test

    def add_existing_test(self, test: Test) -> None:
        self.tests.append(test)

    def find_test(self, name: str) -> Optional[Test]:
        for t in self.tests:
            if t.name.lower() == name.lower():
                return t
        return None

    def show_all_tests(self) -> None:
        if not self.tests:
            print("У редакторі ще немає жодного тесту.")
            return
        print("\nПерелік тестів:")
        for i, t in enumerate(self.tests, start=1):
            print(f"{i}. {t.name} ({len(t.questions)} питань)")

    def delete_test(self, index: int) -> None:
        if 0 <= index < len(self.tests):
            self.tests.pop(index)
        else:
            print("Неправильний номер тесту для видалення.")

    def global_search_questions(self, keyword: str) -> None:
        found_any = False
        for test in self.tests:
            found = [q for q in test.questions if keyword.lower() in q.text.lower()]
            if found:
                found_any = True
                print(f"\nУ тесті '{test.name}' знайдено:")
                for i, q in enumerate(found, start=1):
                    print(f"  {i}. {q.text}")
        if not found_any:
            print("Нічого не знайдено.")


if __name__ == "__main__":
    editor = TestEditor()
