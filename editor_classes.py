from typing import List
import random

class TestEditor:
    def __init__(self):
        self.questions: List[object] = []

    def add_question(self, question):
        self.questions.append(question)
        print(f"[+] Додано питання: {question.text}")

    def show_all(self):
        if not self.questions:
            print("Питань поки що немає.")
            return
        print("\nУсі питання тесту:")
        for i, q in enumerate(self.questions, 1):
            print(f"{i}. {q.text}")

    def edit_question(self, index: int, new_text: str):
        if 0 <= index < len(self.questions):
            old_text = self.questions[index].text
            self.questions[index].text = new_text
            print(f"[~] Питання №{index + 1} змінено:\n    '{old_text}' → '{new_text}'")
        else:
            print("Неправильний номер питання.")

    def delete_question(self, index: int):
        if 0 <= index < len(self.questions):
            removed = self.questions.pop(index)
            print(f"[-] Питання '{removed.text}' видалено.")
        else:
            print("Неправильний номер питання.")

    def find_question(self, keyword: str):
        found = [q for q in self.questions if keyword.lower() in q.text.lower()]
        if found:
            print(f"\nЗнайдено за '{keyword}':")
            for i, q in enumerate(found, 1):
                print(f"{i}. {q.text}")
        else:
            print("Нічого не знайдено.")

    def sort_questions(self):
        self.questions.sort(key=lambda q: q.text.lower())
        print("[*] Питання відсортовано за алфавітом.")

    def shuffle_questions(self):
        random.shuffle(self.questions)
        print("[*] Питання перемішано.")

    def change_correct_answer(self, index: int, new_answer):
        if 0 <= index < len(self.questions):
            self.questions[index].correct_answer = new_answer
            print(f"[~] Правильну відповідь для питання №{index + 1} змінено.")
        else:
            print("Неправильний номер питання.")

    def save_to_file(self, filename: str):
        if not self.questions:
            print("Немає питань для збереження.")
            return
        with open(filename, 'w', encoding='utf-8') as f:
            for q in self.questions:
                f.write(q.text + "\n")
        print(f"Тест збережено у файл '{filename}'.")

    def get_questions(self):
        return self.questions
