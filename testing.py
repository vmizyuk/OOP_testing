import os
import json
import time
import random
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
try:
    from questions_module import (
        Question, SingleChoiceQuestion, MultiChoiceQuestion, TextQuestion,
        ScaleQuestion, TrueFalseQuestion, MatchingQuestion,
        OrderingQuestion, FillBlankQuestion
    )
except ImportError:
    messagebox.showerror("Помилка", "Файл questions_module.py не знадено! Збережіть його в цій же папці.")
    exit()
TESTS_FILE = "tests.json"
RESULTS_FILE = "results.json"
class SessionManager:
    @staticmethod
    def load_tests() -> dict:
        if not os.path.exists(TESTS_FILE):
            return {}
        try:
            with open(TESTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {name: [Question.from_dict(qd) for qd in q_list] for name, q_list in data.items()}
        except Exception:
            return {}
    @staticmethod
    def save_result(test_name: str, user: str, score: float, max_score: int, duration: float, mode: str):
        results = []
        if os.path.exists(RESULTS_FILE):
            try:
                with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                    results = json.load(f)
            except:
                pass
        results.append({
            "test": test_name,
            "user": user,
            "mode": mode,
            "score": round(score, 2),
            "max_score": max_score,
            "duration": round(duration, 1),
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    @staticmethod
    def load_results() -> list:
        if not os.path.exists(RESULTS_FILE):
            return []
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
class QuizRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Проходження Тестів")
        self.root.geometry("550x450")
        self.tests = SessionManager.load_tests()
        self.current_frame = None
        self.show_main_menu()
    def switch_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        if frame_class == MainMenuFrame:
            self.root.geometry("500x350")
        else:
            self.root.geometry("800x650")
        self.current_frame = frame_class(self.root, self, *args)
        self.current_frame.pack(fill="both", expand=True)
    def show_main_menu(self):
        self.tests = SessionManager.load_tests()
        self.switch_frame(MainMenuFrame)
class MainMenuFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tb.Label(self, text="Студентський Портал Тестування", font=("Helvetica", 18, "bold"), bootstyle=PRIMARY).pack(
            pady=50)
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="Почати тестування", width=30, bootstyle=(SUCCESS, OUTLINE),
                  command=lambda: app.switch_frame(TestSetupFrame)).pack(pady=10, ipady=8)
        tb.Button(btn_frame, text="Переглянути статистику", width=30, bootstyle=(INFO, OUTLINE),
                  command=lambda: app.switch_frame(StatisticsFrame)).pack(pady=10, ipady=8)
class TestSetupFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tb.Label(self, text="Налаштування сесії", font=("Helvetica", 16, "bold"), bootstyle=DARK).pack(pady=20)
        if not self.app.tests:
            tb.Label(self, text="Немає доступних тестів.\nПопросіть адміністратора створити їх у Редакторі.",
                     font=("Helvetica", 12), bootstyle=DANGER).pack(pady=20)
            tb.Button(self, text="Назад", bootstyle=SECONDARY, command=app.show_main_menu).pack()
            return
        tb.Label(self, text="Введіть ваше ім'я:", font=("Helvetica", 12)).pack()
        self.user_entry = tb.Entry(self, font=("Helvetica", 12), width=30)
        self.user_entry.pack(pady=5)
        tb.Label(self, text="Оберіть тест:", font=("Helvetica", 12)).pack(pady=(15, 0))
        self.test_var = tb.StringVar(value=list(self.app.tests.keys())[0])
        self.test_combo = tb.Combobox(self, textvariable=self.test_var, values=list(self.app.tests.keys()),
                                      state="readonly", font=("Helvetica", 12), width=28)
        self.test_combo.pack(pady=5)
        tb.Label(self, text="Режим проходження:", font=("Helvetica", 12)).pack(pady=(15, 0))
        self.mode_var = tb.StringVar(value="Звичайний")
        tb.Radiobutton(self, text="Звичайний (Усі питання підряд)", variable=self.mode_var, value="Звичайний",
                       bootstyle=PRIMARY).pack(pady=2)
        tb.Radiobutton(self, text="Адаптивний (Складність змінюється)", variable=self.mode_var, value="Адаптивний",
                       bootstyle=PRIMARY).pack(pady=2)
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=30)
        tb.Button(btn_frame, text="Почати тест", width=15, bootstyle=SUCCESS, command=self.start).pack(side="left",
                                                                                                       padx=10)
        tb.Button(btn_frame, text="Скасувати", width=15, bootstyle=SECONDARY, command=app.show_main_menu).pack(
            side="left", padx=10)
    def start(self):
        user = self.user_entry.get().strip() or "Анонім"
        t_name = self.test_var.get()
        mode = self.mode_var.get()
        questions = self.app.tests[t_name]
        if not questions:
            messagebox.showwarning("Помилка", "Цей тест порожній!")
            return
        self.app.switch_frame(ActiveSessionFrame, t_name, questions, user, mode)
class ActiveSessionFrame(tb.Frame):
    def __init__(self, parent, app, test_name, questions, user, mode):
        super().__init__(parent)
        self.app = app
        self.test_name = test_name
        self.user = user
        self.mode = mode
        self.pool = list(questions)
        self.max_questions = len(self.pool)
        self.asked_count = 0
        self.score = 0.0
        self.current_difficulty = 1
        self.start_time = time.time()
        self.current_q = None
        self.history = []
        info_text = f"Користувач: {user}   |   Тест: {test_name}   |   Режим: {mode}"
        tb.Label(self, text=info_text, font=("Helvetica", 10), bootstyle=(SECONDARY, INVERSE), padding=5).pack(fill="x")
        self.progress_label = tb.Label(self, text="", font=("Helvetica", 12, "bold"), bootstyle=PRIMARY)
        self.progress_label.pack(pady=10)
        self.q_text_label = tb.Label(self, text="", font=("Helvetica", 14), wraplength=550, justify="center",
                                     anchor="center")
        self.q_text_label.pack(pady=20, fill="x", padx=20)
        self.answer_frame = tb.Frame(self)
        self.answer_frame.pack(fill="both", expand=True, padx=40)
        btn_container = tb.Frame(self)
        btn_container.pack(pady=20)
        self.submit_btn = tb.Button(btn_container, text="Відповісти", bootstyle=PRIMARY,
                                    command=self.process_answer)
        self.submit_btn.pack(side="left", padx=10, ipady=5, ipadx=10)
        self.finish_early_btn = tb.Button(btn_container, text="Завершити тест", bootstyle=DANGER,
                                          command=self.finish_test)
        self.finish_early_btn.pack(side="left", padx=10, ipady=5, ipadx=10)
        self.load_next_question()
    def load_next_question(self):
        if self.asked_count >= self.max_questions or not self.pool:
            self.finish_test()
            return
        if self.mode == "Адаптивний":
            suitable = [q for q in self.pool if q.difficulty == self.current_difficulty]
            if not suitable: suitable = self.pool
            self.current_q = random.choice(suitable)
        else:
            self.current_q = random.choice(self.pool)
        self.pool.remove(self.current_q)
        self.asked_count += 1
        self.progress_label.config(
            text=f"Питання {self.asked_count} з {self.max_questions} (Складність: {self.current_q.difficulty})")
        self.q_text_label.config(text=self.current_q.text)
        self.render_answer_inputs()
    def render_answer_inputs(self):
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        self.input_vars = []
        q_type = str(getattr(self.current_q, "q_type", self.current_q.__class__.__name__))
        style = tb.Style()
        style.configure('info.TRadiobutton', font=('Helvetica', 13))
        style.configure('info.TCheckbutton', font=('Helvetica', 13))
        style.configure('success.TRadiobutton', font=('Helvetica', 13))
        style.configure('danger.TRadiobutton', font=('Helvetica', 13))
        inner_frame = tb.Frame(self.answer_frame)
        inner_frame.pack(pady=20)
        if "SingleChoice" in q_type:
            var = tb.StringVar()
            for opt in self.current_q.options:
                tb.Radiobutton(inner_frame, text=opt, variable=var, value=opt, bootstyle=INFO).pack(anchor="w", pady=6)
            self.input_vars.append(var)
        elif "MultiChoice" in q_type:
            for opt in self.current_q.options:
                var = tb.StringVar()
                tb.Checkbutton(inner_frame, text=opt, variable=var, onvalue=opt, offvalue="", bootstyle=INFO).pack(
                    anchor="w", pady=6)
                self.input_vars.append(var)
        elif "Text" in q_type or "FillBlank" in q_type:
            var = tb.StringVar()
            tb.Entry(inner_frame, textvariable=var, font=("Helvetica", 14), width=30).pack(pady=10)
            self.input_vars.append(var)
        elif "Scale" in q_type:
            var = tb.IntVar(value=5)
            val_label = tb.Label(inner_frame, text="Обрано: 5", font=("Helvetica", 13, "bold"))
            val_label.pack(pady=5)
            def update_lbl(event):
                val_label.config(text=f"Обрано: {var.get()}")
            scale = tb.Scale(inner_frame, variable=var, from_=1, to=10, orient="horizontal", length=300,
                             bootstyle=SUCCESS, command=update_lbl)
            scale.pack(pady=10)
            self.input_vars.append(var)
        elif "TrueFalse" in q_type:
            var = tb.BooleanVar()
            tb.Radiobutton(inner_frame, text="Правда", variable=var, value=True, bootstyle=SUCCESS).pack(anchor="w",
                                                                                                         pady=6)
            tb.Radiobutton(inner_frame, text="Брехня", variable=var, value=False, bootstyle=DANGER).pack(anchor="w",
                                                                                                         pady=6)
            self.input_vars.append(var)
        elif "Matching" in q_type:
            terms = list(self.current_q.pairs.keys())
            definitions = list(self.current_q.pairs.values())
            random.shuffle(definitions)
            max_term_len = max([len(str(t)) for t in terms]) if terms else 1
            label_width = max(max_term_len + 1, 3)
            for term in terms:
                row = tb.Frame(inner_frame)
                row.pack(pady=5)
                tb.Label(row, text=term, width=label_width, anchor="e", font=("Helvetica", 12)).pack(side="left",
                                                                                                     padx=(0, 15))
                var = tb.StringVar()
                cb = tb.Combobox(row, textvariable=var, values=definitions, state="readonly", width=30,
                                 font=("Helvetica", 12))
                cb.pack(side="left")
                self.input_vars.append((term, var))
        elif "Ordering" in q_type:
            items = list(self.current_q.correct_order)
            random.shuffle(items)
            tb.Label(inner_frame, text="Оберіть правильну послідовність:", font=("Helvetica", 12, "italic")).pack(
                pady=5)
            for i in range(len(items)):
                row = tb.Frame(inner_frame)
                row.pack(pady=5)
                tb.Label(row, text=f"Позиція {i + 1}:", width=11, anchor="e", font=("Helvetica", 12)).pack(side="left",
                                                                                                           padx=(0, 15))
                var = tb.StringVar()
                cb = tb.Combobox(row, textvariable=var, values=items, state="readonly", width=40,
                                 font=("Helvetica", 12))
                cb.pack(side="left")
                self.input_vars.append(var)
        else:
            tb.Label(inner_frame, text=f"[Цей тип питання ({q_type}) ще не підтримується у GUI]",
                     bootstyle=DANGER).pack()
    def process_answer(self):
        ans = None
        q_type = getattr(self.current_q, "q_type", "Base")
        if q_type in ["SingleChoice", "Text", "FillBlank"]:
            ans = self.input_vars[0].get()
        elif q_type == "MultiChoice":
            ans = [v.get() for v in self.input_vars if v.get()]
        elif q_type in ["Scale", "TrueFalse"]:
            ans = self.input_vars[0].get()
        elif q_type == "Matching":
            ans = {term: var.get() for term, var in self.input_vars}
        elif q_type == "Ordering":
            ans = [var.get() for var in self.input_vars]
        points = self.current_q.check(ans)
        self.score += points
        self.history.append({
            "question": self.current_q.text,
            "user_ans": ans,
            "points": points
        })
        if self.mode == "Адаптивний":
            if points >= 0.8:
                self.current_difficulty = min(3, self.current_difficulty + 1)
            elif points <= 0.2:
                self.current_difficulty = max(1, self.current_difficulty - 1)
        self.load_next_question()
    def finish_test(self):
        duration = time.time() - self.start_time
        SessionManager.save_result(self.test_name, self.user, self.score, self.max_questions, duration, self.mode)
        self.app.switch_frame(ResultDetailsFrame, self.test_name, self.score, self.max_questions, duration,
                              self.history)
class ResultDetailsFrame(tb.Frame):
    def __init__(self, parent, app, test_name, score, max_questions, duration, history):
        super().__init__(parent)
        self.app = app
        tb.Label(self, text="Завершення: Аналіз відповідей", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY).pack(
            pady=15)
        info_text = f"Тест: {test_name}  |  Зароблено балів: {score:.2f} / {max_questions}  |  Час: {duration:.1f} сек."
        tb.Label(self, text=info_text, font=("Helvetica", 12)).pack(pady=5)
        tv_frame = tb.Frame(self)
        tv_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("Питання", "Ваша відповідь", "Бали")
        tree = tb.Treeview(tv_frame, columns=columns, show="headings", height=10, bootstyle=SUCCESS)
        tree.column("Питання", width=380, minwidth=200, stretch=True, anchor="w")
        tree.column("Ваша відповідь", width=250, minwidth=150, stretch=True, anchor="w")
        tree.column("Бали", width=80, minwidth=80, stretch=False, anchor="center")
        for col in columns:
            tree.heading(col, text=col)
        def truncate(text, max_length):
            if len(text) > max_length:
                return text[:max_length] + "..."
            return text
        for item in history:
            ans_str = str(item["user_ans"])
            if isinstance(item["user_ans"], list):
                ans_str = ", ".join(item["user_ans"])
            elif isinstance(item["user_ans"], dict):
                ans_str = " | ".join([f"{k} -> {v}" for k, v in item["user_ans"].items()])
            if not ans_str.strip() or ans_str == "None":
                ans_str = "[Немає відповіді]"
            short_q = truncate(item["question"], 50)
            short_a = truncate(ans_str, 35)
            rounded_points = round(item['points'], 2)
            tree.insert("", "end", values=(short_q, short_a, f"{rounded_points}"))
        v_scrollbar = tb.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tb.Button(self, text="Повернутися до головного меню", bootstyle=PRIMARY, command=app.show_main_menu).pack(
            pady=15)
class StatisticsFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tb.Label(self, text="Глобальна Статистика", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY).pack(pady=15)
        results = SessionManager.load_results()
        if not results:
            tb.Label(self, text="Ще немає жодних результатів.", font=("Helvetica", 12)).pack(pady=20)
        else:
            columns = ("Тест", "Користувач", "Режим", "Бали", "Час (с)", "Дата")
            tree = tb.Treeview(self, columns=columns, show="headings", height=12, bootstyle=INFO)
            tree.column("Тест", width=260)
            tree.column("Користувач", width=110, anchor="center")
            tree.column("Режим", width=110, anchor="center")
            tree.column("Бали", width=70, anchor="center")
            tree.column("Час (с)", width=70, anchor="center")
            tree.column("Дата", width=140, anchor="center")
            for col in columns:
                tree.heading(col, text=col)
            for r in reversed(results):
                tree.insert("", "end",
                            values=(r["test"], r["user"], r["mode"], f"{r['score']}/{r['max_score']}", r["duration"],
                                    r["date"]))
            tree.pack(fill="both", expand=True, padx=15, pady=10)
            avg = sum(r["score"] for r in results) / len(results)
            tb.Label(self, text=f"Загальний середній бал: {avg:.2f}", font=("Helvetica", 12, "bold"),
                     bootstyle=SUCCESS).pack(pady=5)
        tb.Button(self, text="Повернутися до меню", bootstyle=SECONDARY, command=app.show_main_menu).pack(pady=15)
if __name__ == "__main__":
    root = tb.Window(themename="cosmo")
    app = QuizRunnerApp(root)
    root.mainloop()