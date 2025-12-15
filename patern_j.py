from abc import ABC, abstractmethod

class AnswerCheckStrategy(ABC):
    @abstractmethod
    def check(self, correct_answer, user_answer):
        pass


class ExactMatchStrategy(AnswerCheckStrategy):
    def check(self, correct_answer, user_answer):
        return user_answer.strip().lower() == correct_answer.lower()


class PartialMatchStrategy(AnswerCheckStrategy):
    def check(self, correct_answer, user_answer):
        user = user_answer.strip().lower()
        correct = correct_answer.lower()
        return user == correct or user in correct

class Question(ABC):
    def __init__(self, text, topic="", difficulty=1):
        self.text = text
        self.topic = topic
        self.difficulty = difficulty

    @abstractmethod
    def show_question(self):
        pass

    @abstractmethod
    def check_answer(self, user_answer):
        pass

class TextQuestion(Question):
    def __init__(self, text, correct_answer, strategy: AnswerCheckStrategy, topic="", difficulty=1):
        super().__init__(text, topic, difficulty)
        self.correct_answer = correct_answer
        self.strategy = strategy

    def show_question(self):
        print(self.text)

    def check_answer(self, user_answer):
        return self.strategy.check(self.correct_answer, user_answer)

class ChoiceQuestion(Question):
    def __init__(self, text, options, correct_index, topic="", difficulty=1):
        super().__init__(text, topic, difficulty)
        self.options = options
        self.correct_index = correct_index

    def show_question(self):
        print(self.text)
        for i, opt in enumerate(self.options, start=1):
            print(f"{i}. {opt}")

    def check_answer(self, user_answer):
        try:
            return int(user_answer) == self.correct_index
        except ValueError:
            return False

class MatchingQuestion(Question):
    def __init__(self, text, pairs: dict, topic="", difficulty=2):
        super().__init__(text, topic, difficulty)
        self.pairs = pairs

    def show_question(self):
        print(self.text)
        print("Формат: A=1,B=2")
        for k in self.pairs:
            print(f"{k} -> ?")

    def check_answer(self, user_answer: dict):
        return all(
            k in user_answer and user_answer[k].lower() == v.lower()
            for k, v in self.pairs.items()
        )

class QuestionFactory:
    @staticmethod
    def create_question(q_type, **kwargs):
        if q_type == "text_exact":
            return TextQuestion(strategy=ExactMatchStrategy(), **kwargs)
        if q_type == "text_partial":
            return TextQuestion(strategy=PartialMatchStrategy(), **kwargs)
        if q_type == "choice":
            return ChoiceQuestion(**kwargs)
        if q_type == "matching":
            return MatchingQuestion(**kwargs)
        raise ValueError("Невідомий тип питання")

class Quiz:
    def __init__(self, title):
        self.title = title
        self.questions = []

    def add_question(self, question: Question):
        self.questions.append(question)

    def start(self):
        print(f"\n=== {self.title} ===")
        score = 0

        for q in self.questions:
            q.show_question()
            if isinstance(q, MatchingQuestion):
                raw = input("Ваша відповідь: ")
                answer = {
                    item.split('=')[0].strip(): item.split('=')[1].strip()
                    for item in raw.split(',')
                }
            else:
                answer = input("Ваша відповідь: ")

            if q.check_answer(answer):
                print("Вірно!\n")
                score += 1
            else:
                print("Невірно.\n")

        print(f"Результат: {score}/{len(self.questions)}")
        return score

class User:
    def __init__(self, name):
        self.name = name

    def pass_quiz(self, quiz: Quiz):
        print(f"Користувач: {self.name}")
        quiz.start()
