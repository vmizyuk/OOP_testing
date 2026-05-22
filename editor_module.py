import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

try:
    from questions_module import Question, SingleChoiceQuestion, MultiChoiceQuestion, TextQuestion, ScaleQuestion
except ImportError:
    messagebox.showerror("Помилка",
                         "Файл questions_module.py не знайдено в цій папці!")
    exit()

TESTS_FILE = "tests.json"

class DataManager:
    @staticmethod
    def load_tests() -> dict:
        if not os.path.exists(TESTS_FILE):
            return {}
        try:
            with open(TESTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            tests = {}
            for test_name, q_list in data.items():
                tests[test_name] = [Question.from_dict(qd) for qd in q_list]
            return tests
        except Exception as e:
            messagebox.showerror("Помилка читання", f"Не вдалося завантажити тести: {e}")
            return {}

    @staticmethod
    def save_tests(tests_dict: dict):
        data_to_save = {}
        for test_name, q_list in tests_dict.items():
            data_to_save[test_name] = [q.to_dict() for q in q_list]

        with open(TESTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)


class TestEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор Тестів (Режим Адміністратора)")
        self.root.geometry("800x500")

        self.tests = DataManager.load_tests()
        self.current_test_name = None

        self.setup_ui()
        self.refresh_test_list()

    def setup_ui(self):
        left_frame = tk.Frame(self.root, width=250, bg="#f0f0f0", relief="sunken", borderwidth=1)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(left_frame, text="Список тестів", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)

        self.test_listbox = tk.Listbox(left_frame, font=("Arial", 11))
        self.test_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.test_listbox.bind("<<ListboxSelect>>", self.on_test_select)

        btn_frame_left = tk.Frame(left_frame, bg="#f0f0f0")
        btn_frame_left.pack(fill="x", pady=5)
        tk.Button(btn_frame_left, text="Новий тест", command=self.create_test).pack(side="left", padx=5, expand=True,
                                                                                      fill="x")
        tk.Button(btn_frame_left, text="Видалити", command=self.delete_test).pack(side="right", padx=5, expand=True,
                                                                                    fill="x")

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.test_title_label = tk.Label(self.right_frame, text="Виберіть тест зі списку", font=("Arial", 14, "bold"))
        self.test_title_label.pack(pady=10)

        self.questions_tree = ttk.Treeview(self.right_frame, columns=("Type", "Text", "Difficulty"), show="headings")
        self.questions_tree.heading("Type", text="Тип")
        self.questions_tree.heading("Text", text="Питання")
        self.questions_tree.heading("Difficulty", text="Складність")
        self.questions_tree.column("Type", width=100)
        self.questions_tree.column("Text", width=300)
        self.questions_tree.column("Difficulty", width=80)
        self.questions_tree.pack(fill="both", expand=True)

        btn_frame_right = tk.Frame(self.right_frame)
        btn_frame_right.pack(fill="x", pady=10)

        tk.Button(btn_frame_right, text="Додати питання", bg="#d4edda", font=("Arial", 11),
                  command=self.add_question).pack(side="left", padx=5)
        tk.Button(btn_frame_right, text="Видалити питання", bg="#f8d7da", font=("Arial", 11),
                  command=self.delete_question).pack(side="left", padx=5)
        tk.Button(btn_frame_right, text="Зберегти зміни", bg="#cce5ff", font=("Arial", 11, "bold"),
                  command=self.save_all).pack(side="right", padx=5)

    def refresh_test_list(self):
        self.test_listbox.delete(0, tk.END)
        for t_name in self.tests.keys():
            self.test_listbox.insert(tk.END, t_name)

    def on_test_select(self, event):
        selection = self.test_listbox.curselection()
        if not selection: return
        self.current_test_name = self.test_listbox.get(selection[0])
        self.test_title_label.config(text=f"Тест: {self.current_test_name}")
        self.refresh_questions_list()

    def create_test(self):
        name = simpledialog.askstring("Новий тест", "Введіть назву тесту:")
        if name:
            if name in self.tests:
                messagebox.showwarning("Увага", "Тест з такою назвою вже існує!")
                return
            self.tests[name] = []
            self.refresh_test_list()
            self.test_listbox.selection_set(tk.END)
            self.on_test_select(None)

    def delete_test(self):
        if not self.current_test_name: return
        if messagebox.askyesno("Підтвердження", f"Видалити тест '{self.current_test_name}'?"):
            del self.tests[self.current_test_name]
            self.current_test_name = None
            self.test_title_label.config(text="Виберіть тест зі списку")
            self.refresh_test_list()
            self.refresh_questions_list()

    def refresh_questions_list(self):
        for row in self.questions_tree.get_children():
            self.questions_tree.delete(row)

        if not self.current_test_name: return

        for idx, q in enumerate(self.tests[self.current_test_name]):
            self.questions_tree.insert("", "end", iid=str(idx), values=(q.q_type, q.text, q.difficulty))

    def delete_question(self):
        selection = self.questions_tree.selection()
        if not selection: return
        idx = int(selection[0])
        del self.tests[self.current_test_name][idx]
        self.refresh_questions_list()

    def add_question(self):
        if not self.current_test_name:
            messagebox.showwarning("Увага", "Спочатку виберіть або створіть тест!")
            return
        QuestionBuilderDialog(self.root, self)

    def save_all(self):
        DataManager.save_tests(self.tests)
        messagebox.showinfo("Успіх", "Усі тести успішно збережено у файл tests.json!")


class QuestionBuilderDialog(tk.Toplevel):
    def __init__(self, parent, editor_app):
        super().__init__(parent)
        self.editor_app = editor_app
        self.title("Конструктор питання")
        self.geometry("450x450")
        self.grab_set()

        tk.Label(self, text="Тип питання:", font=("Arial", 10, "bold")).pack(pady=5)
        self.type_var = tk.StringVar(value="SingleChoice")
        self.type_combo = ttk.Combobox(self, textvariable=self.type_var, state="readonly",
                                       values=["SingleChoice", "MultiChoice", "Text", "Scale"])
        self.type_combo.pack()
        self.type_combo.bind("<<ComboboxSelected>>", self.build_dynamic_ui)

        tk.Label(self, text="Текст питання:", font=("Arial", 10, "bold")).pack(pady=5)
        self.text_entry = tk.Text(self, height=3, width=50)
        self.text_entry.pack()

        tk.Label(self, text="Складність (1-3):", font=("Arial", 10, "bold")).pack(pady=5)
        self.diff_var = tk.IntVar(value=1)
        tk.Spinbox(self, from_=1, to=3, textvariable=self.diff_var, width=5).pack()

        self.dynamic_frame = tk.Frame(self)
        self.dynamic_frame.pack(fill="both", expand=True, pady=10)

        tk.Button(self, text="Додати до тесту", bg="#d4edda", font=("Arial", 11, "bold"),
                  command=self.save_question).pack(pady=10)

        self.build_dynamic_ui()

    def build_dynamic_ui(self, event=None):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        q_type = self.type_var.get()

        if q_type == "SingleChoice":
            tk.Label(self.dynamic_frame, text="Варіанти відповідей (кожен з нового рядка):").pack()
            self.options_text = tk.Text(self.dynamic_frame, height=4, width=40)
            self.options_text.pack()
            tk.Label(self.dynamic_frame, text="Правильна відповідь (одна з вищевказаних):").pack()
            self.correct_entry = tk.Entry(self.dynamic_frame, width=40)
            self.correct_entry.pack()

        elif q_type == "MultiChoice":
            tk.Label(self.dynamic_frame, text="Варіанти відповідей (кожен з нового рядка):").pack()
            self.options_text = tk.Text(self.dynamic_frame, height=4, width=40)
            self.options_text.pack()
            tk.Label(self.dynamic_frame, text="Правильні відповіді (через кому):").pack()
            self.correct_entry = tk.Entry(self.dynamic_frame, width=40)
            self.correct_entry.pack()

        elif q_type == "Text":
            tk.Label(self.dynamic_frame, text="Ключові слова для перевірки (через кому):").pack()
            self.keywords_entry = tk.Entry(self.dynamic_frame, width=40)
            self.keywords_entry.pack()

        elif q_type == "Scale":
            tk.Label(self.dynamic_frame, text="Правильне числове значення:").pack()
            self.val_entry = tk.Entry(self.dynamic_frame, width=10)
            self.val_entry.pack()
            tk.Label(self.dynamic_frame, text="Допустима похибка (наприклад, 1):").pack()
            self.tol_entry = tk.Entry(self.dynamic_frame, width=10)
            self.tol_entry.pack()

    def save_question(self):
        q_text = self.text_entry.get("1.0", tk.END).strip()
        if not q_text:
            messagebox.showwarning("Увага", "Введіть текст питання!")
            return

        difficulty = self.diff_var.get()
        q_type = self.type_var.get()
        new_q = None

        try:
            if q_type == "SingleChoice":
                options = [opt.strip() for opt in self.options_text.get("1.0", tk.END).strip().split('\n') if
                           opt.strip()]
                correct = self.correct_entry.get().strip()
                new_q = SingleChoiceQuestion(q_text, options, correct, difficulty)

            elif q_type == "MultiChoice":
                options = [opt.strip() for opt in self.options_text.get("1.0", tk.END).strip().split('\n') if
                           opt.strip()]
                correct_list = [c.strip() for c in self.correct_entry.get().split(',') if c.strip()]
                new_q = MultiChoiceQuestion(q_text, options, correct_list, difficulty)

            elif q_type == "Text":
                keywords = [k.strip() for k in self.keywords_entry.get().split(',') if k.strip()]
                new_q = TextQuestion(q_text, keywords, difficulty)

            elif q_type == "Scale":
                val = int(self.val_entry.get().strip())
                tol = int(self.tol_entry.get().strip())
                new_q = ScaleQuestion(q_text, val, tol, difficulty)

            self.editor_app.tests[self.editor_app.current_test_name].append(new_q)
            self.editor_app.refresh_questions_list()
            self.destroy()  # Закриваємо вікно конструктора

        except Exception as e:
            messagebox.showerror("Помилка введення", f"Перевірте правильність заповнення полів!\nДеталі: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TestEditorApp(root)
    root.mainloop()