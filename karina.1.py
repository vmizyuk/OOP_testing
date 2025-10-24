import time
import random

class Question:
    def __init__(self, text, options=None, correct=None, difficulty=1, topic="general"):
        self.text = text
        self.options = options or []
        self.correct = correct
        self.difficulty = difficulty
        self.topic = topic

    def ask(self):
        print("\nПитання:", self.text)
        if self.options:
            for i, opt in enumerate(self.options, 1):
                print(f"{i}. {opt}")
        start_time = time.time()
        answer = input("Ваша відповідь: ").strip()
        end_time = time.time()
        return answer, end_time - start_time


class TestSystem:
    def __init__(self):
        self.questions = []
        self.results = []

    def add_question(self, question):
        self.questions.append(question)

    def start_test(self):
        print("\n=== Початок тестування ===")
        score = 0
        total_time = 0
        asked = []
        difficulty = 1  # початкова складність

        for _ in range(5):  # кількість питань можна змінити
            available = [q for q in self.questions if q.difficulty == difficulty and q not in asked]
            if not available:
                available = self.questions  # якщо немає питань цієї складності

            question = random.choice(available)
            asked.append(question)
            answer, duration = question.ask()
            total_time += duration

            if answer.lower() == str(question.correct).lower():
                print("Правильно!")
                score += 1
                difficulty = min(3, difficulty + 1)
            else:
                print(f"Неправильно. Правильна відповідь: {question.correct}")
                difficulty = max(1, difficulty - 1)

        print("\n=== Результати ===")
        print(f"Ваш бал: {score}/{len(asked)}")
        print(f"Середній час на питання: {total_time / len(asked):.2f} сек")

        self.results.append({"score": score, "time": total_time})

    def show_statistics(self):
        if not self.results:
            print("Немає даних для статистики.")
            return
        avg_score = sum(r["score"] for r in self.results) / len(self.results)
        avg_time = sum(r["time"] for r in self.results) / len(self.results)
        print("\n=== Статистика тестів ===")
        print(f"Кількість тестів: {len(self.results)}")
        print(f"Середній бал: {avg_score:.2f}")
        print(f"Середній час проходження: {avg_time:.2f} сек")
