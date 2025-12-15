import time
import random
import json

class Question:
    def __init__(self, text, options=None, correct=None, difficulty=1, topic="general"):
        self.text = text
        self.options = options or []
        self.correct = correct
        self.difficulty = difficulty
        self.topic = topic
    def ask(self):
        print("\n────────────────────────────────────────")
        print(self.text)
        print("────────────────────────────────────────")

        if self.options:
            for i, opt in enumerate(self.options, 1):
                print(f"{i}) {opt}")

        start = time.time()
        answer = input("\nВаша відповідь: ").strip()
        end = time.time()

        return answer, end - start


class TestSystem:
    def __init__(self):
        self.questions = []
        self.results = []

    def add_question(self, question):
        self.questions.append(question)

    def welcome_screen(self):
        print("========================================")
        print("               ТЕСТУВАННЯ               ")
        print("========================================")
        input("Натисніть Enter, щоб почати...")

    def finish_screen(self, score, total, avg_time):
        print("\n========================================")
        print("               РЕЗУЛЬТАТИ               ")
        print("========================================")
        print(f"Правильних відповідей: {score}/{total}")
        print(f"Середній час: {avg_time:.2f} сек")
        print("========================================\n")

    def start_test(self):
        if not self.questions:
            print("У списку немає питань!")
            return

        self.welcome_screen()

        score = 0
        total_time = 0
        asked = []
        difficulty = 1

        for _ in range(5):
            available = [q for q in self.questions if q.difficulty == difficulty and q not in asked]

            if not available:
                available = [q for q in self.questions if q not in asked]

            question = random.choice(available)
            asked.append(question)

            answer, duration = question.ask()
            total_time += duration

            if answer.lower() == str(question.correct).lower():
                print("Правильно!\n")
                score += 1
                difficulty = min(3, difficulty + 1)
            else:
                print(f"Неправильно! Правильна відповідь: {question.correct}\n")
                difficulty = max(1, difficulty - 1)

            input("Натисніть Enter для наступного питання...")

        avg_time = total_time / len(asked)
        self.results.append({"score": score, "time": total_time})
        self.finish_screen(score, len(asked), avg_time)

    def show_statistics(self):
        if not self.results:
            print("Статистика пуста.")
            return

        avg_score = sum(r["score"] for r in self.results) / len(self.results)
        avg_time = sum(r["time"] for r in self.results) / len(self.results)

        print("\nСтатистика:")
        print(f"Тестів пройдено: {len(self.results)}")
        print(f"Середній бал: {avg_score:.2f}")
        print(f"Середній час: {avg_time:.2f} сек")

    def save_questions(self, filename="questions.json"):
        data = [{
            "text": q.text,
            "options": q.options,
            "correct": q.correct,
            "difficulty": q.difficulty,
            "topic": q.topic
        } for q in self.questions]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print("Питання збережено.")

    def load_questions(self, filename="questions.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            for d in data:
                q = Question(
                    text=d["text"],
                    options=d["options"],
                    correct=d["correct"],
                    difficulty=d["difficulty"],
                    topic=d["topic"]
                )
                self.questions.append(q)

            print("Питання завантажено.")
        except FileNotFoundError:
            print("Файл не знайдено.")

    def menu(self):
        while True:
            print("\n================ МЕНЮ ================")
            print("1) Почати тест")
            print("2) Переглянути статистику")
            print("3) Завантажити питання")
            print("4) Зберегти питання")
            print("5) Вийти")
            print("======================================")

            choice = input("Ваш вибір: ").strip()

            if choice == "1":
                self.start_test()
            elif choice == "2":
                self.show_statistics()
            elif choice == "3":
                self.load_questions()
            elif choice == "4":
                self.save_questions()
            elif choice == "5":
                print("Вихід...")
                break
            else:
                print("Невірний вибір — спробуйте ще раз.")

