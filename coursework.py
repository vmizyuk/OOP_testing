import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import time
import random

# Імпортуємо класи з файлу першої учасниці
try:
    from questions_module import Question, SingleChoiceQuestion, MultiChoiceQuestion, TextQuestion, ScaleQuestion, \
        TrueFalseQuestion
except ImportError:
    messagebox.showerror("Помилка", "Файл questions_module.py не знайдено! Збережіть його в цій же папці.")
    exit()
TESTS_FILE = "tests.json"
RESULTS_FILE = "results.json"


# ==========================================
# 1. МЕНЕДЖЕР ДАНИХ (Для Тесту та Статистики)
# ==========================================
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
        if not os.path.exists(RESULTS_FILE): return []
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


# ==========================================
# 2. ГОЛОВНИЙ ДОДАТОК ТЕСТУВАННЯ
# ==========================================
class QuizRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Проходження Тестів")
        self.root.geometry("650x500")
        self.tests = SessionManager.load_tests()

        self.current_frame = None
        self.show_main_menu()

    def switch_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_main_menu(self):
        self.tests = SessionManager.load_tests()  # Оновлюємо тести при виході в меню
        self.switch_frame(MainMenuFrame)


# ==========================================
# 3. ІНТЕРФЕЙС: ГОЛОВНЕ МЕНЮ ТА НАЛАШТУВАННЯ
# ==========================================
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Студентський Портал Тестування", font=("Arial", 18, "bold")).pack(pady=40)
        tk.Button(self, text="Почати тестування", font=("Arial", 14), width=25, bg="#d4edda",
                  command=lambda: app.switch_frame(TestSetupFrame)).pack(pady=10)
        tk.Button(self, text="Переглянути статистику", font=("Arial", 14), width=25, bg="#cce5ff",
                  command=lambda: app.switch_frame(StatisticsFrame)).pack(pady=10)


class TestSetupFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Налаштування сесії", font=("Arial", 16, "bold")).pack(pady=20)
        if not self.app.tests:
            tk.Label(self, text="Немає доступних тестів.\nПопросіть адміністратора створити їх у Редакторі.", fg="red",
                     font=("Arial", 12)).pack(pady=20)
            tk.Button(self, text="Назад", command=app.show_main_menu).pack()
            return
        tk.Label(self, text="Введіть ваше ім'я:", font=("Arial", 12)).pack()
        self.user_entry = tk.Entry(self, font=("Arial", 12), width=30)
        self.user_entry.pack(pady=5)
        tk.Label(self, text="Оберіть тест:", font=("Arial", 12)).pack(pady=(10, 0))
        self.test_var = tk.StringVar(value=list(self.app.tests.keys())[0])
        self.test_combo = ttk.Combobox(self, textvariable=self.test_var, values=list(self.app.tests.keys()),
                                       state="readonly", font=("Arial", 12), width=28)
        self.test_combo.pack(pady=5)
        tk.Label(self, text="Режим проходження:", font=("Arial", 12)).pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="Звичайний")
        tk.Radiobutton(self, text="Звичайний (Усі питання підряд)", variable=self.mode_var, value="Звичайний",
                       font=("Arial", 11)).pack()
        tk.Radiobutton(self, text="Адаптивний (Складність змінюється від відповідей)", variable=self.mode_var,
                       value="Адаптивний", font=("Arial", 11)).pack()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Почати тест", font=("Arial", 12, "bold"), bg="#28a745", fg="white",
                  command=self.start).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Скасувати", font=("Arial", 12), command=app.show_main_menu).pack(side="left",
                                                                                                    padx=10)

    def start(self):
        user = self.user_entry.get().strip() or "Анонім"
        t_name = self.test_var.get()
        mode = self.mode_var.get()
        questions = self.app.tests[t_name]

        if not questions:
            messagebox.showwarning("Помилка", "Цей тест порожній!")
            return

        self.app.switch_frame(ActiveSessionFrame, t_name, questions, user, mode)


# ==========================================
# 4. ІНТЕРФЕЙС: АКТИВНА СЕСІЯ ТЕСТУВАННЯ
# ==========================================
class ActiveSessionFrame(tk.Frame):
    def __init__(self, parent, app, test_name, questions, user, mode):
        super().__init__(parent)
        self.app = app
        self.test_name = test_name
        self.user = user
        self.mode = mode

        self.pool = list(questions)
        # У звичайному режимі проходимо всі питання, в адаптивному — максимум 5
        self.max_questions = len(self.pool) if mode == "Звичайний" else min(5, len(self.pool))

        self.asked_count = 0
        self.score = 0.0
        self.current_difficulty = 1
        self.start_time = time.time()
        self.current_q = None
        # Верхня панель (Інфо)
        info_text = f"Користувач: {user} | Тест: {test_name} | Режим: {mode}"
        tk.Label(self, text=info_text, bg="#e9ecef", font=("Arial", 10)).pack(fill="x", pady=5)

        self.progress_label = tk.Label(self, text="", font=("Arial", 12, "bold"), fg="#0056b3")
        self.progress_label.pack(pady=5)
        # Зона питання
        self.q_text_label = tk.Label(self, text="", font=("Arial", 14), wraplength=550, justify="center")
        self.q_text_label.pack(pady=20, fill="x")
        # Зона відповідей (динамічна)
        self.answer_frame = tk.Frame(self)
        self.answer_frame.pack(fill="both", expand=True, padx=40)
        self.submit_btn = tk.Button(self, text="Підтвердити відповідь", font=("Arial", 12, "bold"), bg="#007bff",
                                    fg="white", command=self.process_answer)
        self.submit_btn.pack(pady=20)
        self.load_next_question()

    def load_next_question(self):
        if self.asked_count >= self.max_questions or not self.pool:
            self.finish_test()
            return
        # Логіка вибору питання
        if self.mode == "Адаптивний":
            # Шукаємо питання поточної складності
            suitable = [q for q in self.pool if q.difficulty == self.current_difficulty]
            if not suitable: suitable = self.pool  # Якщо таких немає, беремо будь-яке
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
        q_type = getattr(self.current_q, "q_type", "Base")
        if q_type == "SingleChoice":
            var = tk.StringVar()
            for opt in self.current_q.options:
                tk.Radiobutton(self.answer_frame, text=opt, variable=var, value=opt, font=("Arial", 12)).pack(
                    anchor="w", pady=2)
            self.input_vars.append(var)
        elif q_type == "MultiChoice":
            for opt in self.current_q.options:
                var = tk.StringVar()
                tk.Checkbutton(self.answer_frame, text=opt, variable=var, onvalue=opt, offvalue="",
                               font=("Arial", 12)).pack(anchor="w", pady=2)
                self.input_vars.append(var)
        elif q_type in ["Text", "FillBlank"]:
            var = tk.StringVar()
            tk.Entry(self.answer_frame, textvariable=var, font=("Arial", 14), width=30).pack(pady=10)
            self.input_vars.append(var)
        elif q_type == "Scale":
            var = tk.IntVar(value=5)  # Середнє значення за замовчуванням
            tk.Scale(self.answer_frame, variable=var, from_=1, to=10, orient="horizontal", length=300,
                     tickinterval=1).pack(pady=10)
            self.input_vars.append(var)
        elif q_type == "TrueFalse":
            var = tk.BooleanVar()
            tk.Radiobutton(self.answer_frame, text="Правда", variable=var, value=True, font=("Arial", 12)).pack(
                anchor="w", pady=5)
            tk.Radiobutton(self.answer_frame, text="Брехня", variable=var, value=False, font=("Arial", 12)).pack(
                anchor="w", pady=5)
            self.input_vars.append(var)
        else:
            tk.Label(self.answer_frame, text="[Цей тип питання ще не підтримується у GUI]", fg="red").pack()

    def process_answer(self):
        # Зчитуємо відповідь
        ans = None
        q_type = getattr(self.current_q, "q_type", "Base")
        if q_type in ["SingleChoice", "Text", "FillBlank"]:
            ans = self.input_vars[0].get()
        elif q_type == "MultiChoice":
            ans = [v.get() for v in self.input_vars if v.get()]
        elif q_type in ["Scale", "TrueFalse"]:
            ans = self.input_vars[0].get()
        # Оцінюємо
        points = self.current_q.check(ans)
        self.score += points
        # Адаптація складності
        if self.mode == "Адаптивний":
            if points >= 0.8:  # Відповів добре -> ускладнюємо
                self.current_difficulty = min(3, self.current_difficulty + 1)
            elif points <= 0.2:  # Відповів погано -> полегшуємо
                self.current_difficulty = max(1, self.current_difficulty - 1)
        self.load_next_question()

    def finish_test(self):
        duration = time.time() - self.start_time
        SessionManager.save_result(self.test_name, self.user, self.score, self.max_questions, duration, self.mode)

        msg = f"Тестування завершено!\n\nЗароблено балів: {self.score:.2f} з {self.max_questions}\nЧас проходження: {duration:.1f} сек."
        messagebox.showinfo("Результат", msg)
        self.app.show_main_menu()


# ==========================================
# 5. ІНТЕРФЕЙС: СТАТИСТИКА
# ==========================================
class StatisticsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Глобальна Статистика", font=("Arial", 16, "bold")).pack(pady=10)
        results = SessionManager.load_results()

        if not results:
            tk.Label(self, text="Ще немає жодних результатів.").pack(pady=20)
        else:
            # Створення таблиці
            columns = ("Тест", "Користувач", "Режим", "Бали", "Час (с)", "Дата")
            tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

            tree.column("Тест", width=120)
            tree.column("Користувач", width=100)
            tree.column("Режим", width=100)
            tree.column("Бали", width=60, anchor="center")
            tree.column("Час (с)", width=60, anchor="center")
            tree.column("Дата", width=140)
            for col in columns:
                tree.heading(col, text=col)
            for r in reversed(results):  # Останні зверху
                tree.insert("", "end",
                            values=(r["test"], r["user"], r["mode"], f"{r['score']}/{r['max_score']}", r["duration"],
                                    r["date"]))

            tree.pack(fill="both", expand=True, padx=10, pady=10)
            # Розрахунок середнього бала
            avg = sum(r["score"] for r in results) / len(results)
            tk.Label(self, text=f"Загальний середній бал по всій системі: {avg:.2f}", font=("Arial", 12, "bold"),
                     fg="#28a745").pack(pady=5)
        tk.Button(self, text="Повернутися до меню", font=("Arial", 12), command=app.show_main_menu).pack(pady=10)


# ==========================================
# ЗАПУСК ДОДАТКУ
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizRunnerApp(root)
    root.mainloop()