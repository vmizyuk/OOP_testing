from abc import ABC, abstractmethod


class Question(ABC):
    def __init__(self, text, correct_answer):
        self.text = text
        self.correct_answer = correct_answer

    @abstractmethod
    def check_answer(self, user_answer):
        pass

    def show_question(self):
        print(f"Питання: {self.text}")


class TextQuestion(Question):
    def __init__(self, text, correct_answer, partial_allowed=True):
        super().__init__(text, correct_answer)
        self.partial_allowed = partial_allowed

    def check_answer(self, user_answer):
        user_answer = user_answer.strip().lower()
        correct = self.correct_answer.lower()
        if user_answer == correct:
            return True
        if self.partial_allowed and user_answer in correct:
            return True
        return False


class ChoiceQuestion(Question):
    def __init__(self, text, options, correct_answer):
        super().__init__(text, correct_answer)
        self.options = options

    def show_question(self):
        print(f"Питання: {self.text}")
        for i, option in enumerate(self.options, start=1):
            print(f"  {i}. {option}")

    def check_answer(self, user_answer):
        try:
            index = int(user_answer) - 1
            return self.options[index].strip().lower() == self.correct_answer.lower()
        except (ValueError, IndexError):
            return False


class RatingQuestion(Question):
    def __init__(self, text, scale_min, scale_max):
        super().__init__(text, None)
        self.scale_min = scale_min
        self.scale_max = scale_max

    def show_question(self):
        print(f"{self.text} (оцініть від {self.scale_min} до {self.scale_max})")

    def check_answer(self, user_answer):
        try:
            value = int(user_answer)
            return self.scale_min <= value <= self.scale_max
        except ValueError:
            return False


class MatchingQuestion(Question):
    def __init__(self, text, pairs):
        super().__init__(text, pairs)

    def show_question(self):
        print(self.text)
        print("Зіставте елементи:")
        for key in self.correct_answer.keys():
            print(f" - {key} → ?")

    def check_answer(self, user_answer):
        if not isinstance(user_answer, dict):
            return False
        correct_pairs = self.correct_answer
        correct_count = sum(1 for k, v in user_answer.items()
                            if k in correct_pairs and correct_pairs[k].lower() == v.lower())
        return correct_count == len(correct_pairs)


class MultipleChoiceQuestion(Question):
    def __init__(self, text, options, correct_answers):
        super().__init__(text, correct_answers)
        self.options = options

    def show_question(self):
        print(f"Питання: {self.text}")
        for i, option in enumerate(self.options, start=1):
            print(f"  {i}. {option}")
        print("Введіть номери правильних варіантів через кому (наприклад: 1,3)")

    def check_answer(self, user_answer):
        try:
            selected = {int(x.strip()) for x in user_answer.split(',')}
            correct = {self.options.index(ans) + 1 for ans in self.correct_answer}
            return selected == correct
        except Exception:
            return False


if __name__ == "__main__":
    print("=== Тестовий сценарій: Перевірка роботи класів питань ===")

    q1 = TextQuestion("Столиця України?", "Київ")
    q2 = ChoiceQuestion("Яка нова мова програмування?:", ["Python", "C++", "HTML"], "Python")
    q3 = RatingQuestion("Оцініть тест", 1, 5)
    q4 = MatchingQuestion("Встановіть відповідності:", {"Сонце": "Зірка", "Місяць": "Супутник"})
    q5 = MultipleChoiceQuestion("Оберіть мови програмування:", ["Python", "C++", "HTML", "Java"], ["Python", "C++"])

    q1.show_question(); print("→", q1.check_answer("ки"))
    q2.show_question(); print("→", q2.check_answer("1"))
    q3.show_question(); print("→", q3.check_answer("5"))
    q4.show_question(); print("→", q4.check_answer({"Сонце": "Зірка", "Місяць": "Супутник"}))
    q5.show_question(); print("→", q5.check_answer("1,2"))