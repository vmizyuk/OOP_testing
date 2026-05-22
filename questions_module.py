from typing import List, Dict, Any, Union

class Question:
    def __init__(self, text: str, difficulty: int = 1, topic: str = "Загальне"):
        self.text = text
        self.difficulty = difficulty
        self.topic = topic
        self.q_type = "Base"

    def check(self, answer: Any) -> float:
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "q_type": self.q_type,
            "text": self.text,
            "difficulty": self.difficulty,
            "topic": self.topic
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Question':
        q_type = data.get("q_type")
        if q_type == "SingleChoice":
            return SingleChoiceQuestion(data["text"], data["options"], data["correct"], data["difficulty"],
                                        data["topic"])
        elif q_type == "MultiChoice":
            return MultiChoiceQuestion(data["text"], data["options"], data["correct_list"], data["difficulty"],
                                       data["topic"])
        elif q_type == "Text":
            return TextQuestion(data["text"], data["keywords"], data["difficulty"], data["topic"])
        elif q_type == "Scale":
            return ScaleQuestion(data["text"], data["correct_val"], data["tolerance"], data["difficulty"],
                                 data["topic"])
        elif q_type == "TrueFalse":
            return TrueFalseQuestion(data["text"], data["correct_bool"], data["difficulty"], data["topic"])
        elif q_type == "Matching":
            return MatchingQuestion(data["text"], data["pairs"], data["difficulty"], data["topic"])
        elif q_type == "Ordering":
            return OrderingQuestion(data["text"], data["correct_order"], data["difficulty"], data["topic"])
        elif q_type == "FillBlank":
            return FillBlankQuestion(data["text"], data["acceptable_answers"], data["difficulty"], data["topic"])
        else:
            return Question(data["text"], data.get("difficulty", 1), data.get("topic", "Загальне"))


class SingleChoiceQuestion(Question):
    def __init__(self, text: str, options: List[str], correct: str, difficulty: int = 1, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "SingleChoice"
        self.options = options
        self.correct = correct

    def check(self, answer: str) -> float:
        if not answer: return 0.0
        return 1.0 if answer.lower().strip() == self.correct.lower().strip() else 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"options": self.options, "correct": self.correct})
        return data


class MultiChoiceQuestion(Question):
    def __init__(self, text: str, options: List[str], correct_list: List[str], difficulty: int = 2,
                 topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "MultiChoice"
        self.options = options
        self.correct_list = correct_list

    def check(self, answer_list: List[str]) -> float:
        if not answer_list: return 0.0
        correct_hits = sum(1 for a in answer_list if a in self.correct_list)
        wrong_hits = sum(1 for a in answer_list if a not in self.correct_list)

        score = (correct_hits / len(self.correct_list)) - (wrong_hits * 0.5)
        return max(0.0, min(1.0, score))

    def to_dict(self):
        data = super().to_dict()
        data.update({"options": self.options, "correct_list": self.correct_list})
        return data


class TextQuestion(Question):
    def __init__(self, text: str, keywords: List[str], difficulty: int = 2, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "Text"
        self.keywords = [k.lower().strip() for k in keywords]

    def check(self, answer: str) -> float:
        if not answer: return 0.0
        ans_lower = answer.lower()
        matches = sum(1 for k in self.keywords if k in ans_lower)
        return matches / len(self.keywords) if self.keywords else 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"keywords": self.keywords})
        return data


class ScaleQuestion(Question):
    def __init__(self, text: str, correct_val: int, tolerance: int = 1, difficulty: int = 1, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "Scale"
        self.correct_val = correct_val
        self.tolerance = tolerance

    def check(self, answer: Union[int, str]) -> float:
        try:
            val = int(answer)
            diff = abs(val - self.correct_val)
            if diff == 0: return 1.0
            if diff <= self.tolerance: return 0.5
            return 0.0
        except ValueError:
            return 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"correct_val": self.correct_val, "tolerance": self.tolerance})
        return data

class TrueFalseQuestion(Question):
    def __init__(self, text: str, correct_bool: bool, difficulty: int = 1, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "TrueFalse"
        self.correct_bool = correct_bool

    def check(self, answer: bool) -> float:
        return 1.0 if answer == self.correct_bool else 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"correct_bool": self.correct_bool})
        return data


class MatchingQuestion(Question):
    def __init__(self, text: str, pairs: Dict[str, str], difficulty: int = 3, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "Matching"
        self.pairs = pairs

    def check(self, answer_pairs: Dict[str, str]) -> float:
        if not answer_pairs: return 0.0
        correct_count = 0
        for key, value in answer_pairs.items():
            if key in self.pairs and self.pairs[key] == value:
                correct_count += 1
        return correct_count / len(self.pairs) if self.pairs else 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"pairs": self.pairs})
        return data


class OrderingQuestion(Question):
    def __init__(self, text: str, correct_order: List[str], difficulty: int = 3, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "Ordering"
        self.correct_order = correct_order

    def check(self, answer_order: List[str]) -> float:
        if not answer_order or len(answer_order) != len(self.correct_order): return 0.0
        correct_positions = sum(1 for i, item in enumerate(answer_order) if item == self.correct_order[i])
        return correct_positions / len(self.correct_order)

    def to_dict(self):
        data = super().to_dict()
        data.update({"correct_order": self.correct_order})
        return data


class FillBlankQuestion(Question):
    def __init__(self, text: str, acceptable_answers: List[str], difficulty: int = 2, topic: str = "Загальне"):
        super().__init__(text, difficulty, topic)
        self.q_type = "FillBlank"
        self.acceptable_answers = [ans.lower().strip() for ans in acceptable_answers]

    def check(self, answer: str) -> float:
        if not answer: return 0.0
        return 1.0 if answer.lower().strip() in self.acceptable_answers else 0.0

    def to_dict(self):
        data = super().to_dict()
        data.update({"acceptable_answers": self.acceptable_answers})
        return data


if __name__ == "__main__":
    print("Тестування системи оцінювання питань")

    q_multi = MultiChoiceQuestion("Оберіть мови програмування:", ["HTML", "Python", "CSS", "C++"], ["Python", "C++"])
    print(f"\nПитання: {q_multi.text}")
    print(f"Відповідь: ['Python'] -> Оцінка: {q_multi.check(['Python'])} бала (одна правильна з двох = 0.5)")
    print(
        f"Відповідь: ['Python', 'HTML'] -> Оцінка: {q_multi.check(['Python', 'HTML'])} бала (1 правильна - 1 помилка = 0.0)")
    print(f"Відповідь: ['Python', 'C++'] -> Оцінка: {q_multi.check(['Python', 'C++'])} бала (Ідеально)")

    q_scale = ScaleQuestion("Оцініть складність від 1 до 10 (Правильна: 7, Похибка: 1)", correct_val=7, tolerance=1)
    print(f"\nПитання: {q_scale.text}")
    print(f"Відповідь: 7 -> Оцінка: {q_scale.check(7)} бала (Точно)")
    print(f"Відповідь: 8 -> Оцінка: {q_scale.check(8)} бала (Близько, в межах похибки)")
    print(f"Відповідь: 5 -> Оцінка: {q_scale.check(5)} бала (Неправильно)")

    q_match = MatchingQuestion("З'єднайте столиці:", {"Україна": "Київ", "Франція": "Париж", "Італія": "Рим"})
    print(f"\nПитання: {q_match.text}")
    ans_match = {"Україна": "Київ", "Франція": "Ліон", "Італія": "Рим"}
    print(f"Відповідь: {ans_match} -> Оцінка: {q_match.check(ans_match):.2f} бала (66% правильних)")

    print("\nПеревірка збереження у словник")
    q_dict = q_match.to_dict()
    print(q_dict)

    print("\nПеревірка відновлення зі словника")
    restored_q = Question.from_dict(q_dict)
    print(
        f"Відновлений тип: {type(restored_q).__name__}, Бали за правильну відповідь: {restored_q.check({'Україна': 'Київ', 'Франція': 'Париж', 'Італія': 'Рим'})}")