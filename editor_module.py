import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from ttkbootstrap.dialogs import Querybox
import json
import os

try:
    from questions_module import (
        Question, SingleChoiceQuestion, MultiChoiceQuestion, TextQuestion,
        ScaleQuestion, TrueFalseQuestion, MatchingQuestion,
        OrderingQuestion, FillBlankQuestion
    )
except ImportError:
    messagebox.showerror("Помилка", "Файл questions_module.py не знайдено!")
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
        self.root.geometry("900x600")

        self.tests = DataManager.load_tests()
        self.current_test_name = None

        self.setup_ui()
        self.refresh_test_list()

    def setup_ui(self):
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        left_frame = tb.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        tb.Label(left_frame, text="Список тестів", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        self.test_listbox = tb.Treeview(left_frame, show="tree", bootstyle=INFO)
        self.test_listbox.pack(fill="both", expand=True)
        self.test_listbox.bind("<<TreeviewSelect>>", self.on_test_select)

        btn_frame_left = tb.Frame(left_frame)
        btn_frame_left.pack(fill="x", pady=10)

        tb.Button(btn_frame_left, text="Новий тест", bootstyle=(SUCCESS, OUTLINE), command=self.create_test).pack(
            side="left", fill="x", expand=True, padx=(0, 5))
        tb.Button(btn_frame_left, text="Видалити", bootstyle=(DANGER, OUTLINE), command=self.delete_test).pack(
            side="right", fill="x", expand=True)

        right_frame = tb.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.test_title_lbl = tb.Label(right_frame, text="Виберіть тест зі списку", font=("Helvetica", 16, "bold"))
        self.test_title_lbl.pack(pady=(0, 10))

        columns = ("Тип", "Питання", "Складність")
        self.q_tree = tb.Treeview(right_frame, columns=columns, show="headings", bootstyle=PRIMARY)
        self.q_tree.heading("Тип", text="Тип")
        self.q_tree.heading("Питання", text="Текст питання")
        self.q_tree.heading("Складність", text="Складність")

        self.q_tree.column("Тип", width=120, anchor="center")
        self.q_tree.column("Питання", width=350)
        self.q_tree.column("Складність", width=80, anchor="center")
        self.q_tree.pack(fill="both", expand=True)

        btn_frame_right = tb.Frame(right_frame)
        btn_frame_right.pack(fill="x", pady=10)

        tb.Button(btn_frame_right, text="Додати питання", bootstyle=PRIMARY, command=self.add_question).pack(
            side="left", padx=(0, 10))
        tb.Button(btn_frame_right, text="Видалити питання", bootstyle=WARNING, command=self.delete_question).pack(
            side="left")
        tb.Button(btn_frame_right, text="Зберегти зміни", bootstyle=SUCCESS, command=self.save_all).pack(side="right")

    def refresh_test_list(self):
        for item in self.test_listbox.get_children():
            self.test_listbox.delete(item)
        for test_name in self.tests.keys():
            self.test_listbox.insert("", "end", iid=test_name, text=test_name)

    def on_test_select(self, event):
        selected = self.test_listbox.selection()
        if not selected: return
        self.current_test_name = selected[0]
        self.test_title_lbl.config(text=f"Редагування: {self.current_test_name}")
        self.refresh_questions_list()

    def create_test(self):
        name = Querybox.get_string(prompt="Введіть назву нового тесту:", title="Новий тест")
        if name:
            if name in self.tests:
                messagebox.showwarning("Помилка", "Тест з такою назвою вже існує!")
                return
            self.tests[name] = []
            self.refresh_test_list()

    def delete_test(self):
        selected = self.test_listbox.selection()
        if not selected: return
        test_name = selected[0]
        if messagebox.askyesno("Підтвердження", f"Видалити тест '{test_name}'?"):
            del self.tests[test_name]
            self.current_test_name = None
            self.test_title_lbl.config(text="Виберіть тест зі списку")
            self.refresh_test_list()
            self.refresh_questions_list()

    def refresh_questions_list(self):
        for item in self.q_tree.get_children():
            self.q_tree.delete(item)
        if not self.current_test_name: return

        for idx, q in enumerate(self.tests[self.current_test_name]):
            self.q_tree.insert("", "end", iid=str(idx), values=(q.q_type, q.text, q.difficulty))

    def delete_question(self):
        selected = self.q_tree.selection()
        if not selected: return
        idx = int(selected[0])
        if messagebox.askyesno("Підтвердження", "Видалити обране питання?"):
            del self.tests[self.current_test_name][idx]
            self.refresh_questions_list()

    def add_question(self):
        if not self.current_test_name:
            messagebox.showwarning("Помилка", "Спочатку виберіть або створіть тест!")
            return
        QuestionBuilderDialog(self.root, self)

    def save_all(self):
        DataManager.save_tests(self.tests)
        messagebox.showinfo("Збережено", "Усі зміни успішно збережено у файл tests.json!")


class QuestionBuilderDialog(tb.Toplevel):
    def __init__(self, parent, editor_app):
        super().__init__(parent)
        self.editor_app = editor_app
        self.title("Конструктор питання")
        self.geometry("500x550")
        self.grab_set()

        tb.Label(self, text="Тип питання:", font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.type_var = tb.StringVar(value="SingleChoice")
        self.type_combo = tb.Combobox(self, textvariable=self.type_var, state="readonly",
                                      values=["SingleChoice", "MultiChoice", "Text", "Scale",
                                              "TrueFalse", "Matching", "Ordering", "FillBlank"])
        self.type_combo.pack(fill="x", padx=20)
        self.type_combo.bind("<<ComboboxSelected>>", self.build_dynamic_ui)

        tb.Label(self, text="Текст питання:", font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.text_entry = tb.Text(self, height=3)
        self.text_entry.pack(fill="x", padx=20)

        tb.Label(self, text="Складність (1-3):", font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.diff_var = tb.IntVar(value=1)
        tb.Spinbox(self, from_=1, to=3, textvariable=self.diff_var).pack(fill="x", padx=20)

        self.dynamic_frame = tb.Frame(self)
        self.dynamic_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tb.Button(self, text="Додати до тесту", bootstyle=SUCCESS, command=self.save_question).pack(pady=10)

        self.build_dynamic_ui()

    def build_dynamic_ui(self, event=None):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        q_type = self.type_var.get()

        if q_type == "SingleChoice":
            tb.Label(self.dynamic_frame, text="Варіанти (з нового рядка):").pack(anchor="w")
            self.options_text = tb.Text(self.dynamic_frame, height=4)
            self.options_text.pack(fill="x", pady=(0, 10))
            tb.Label(self.dynamic_frame, text="Правильна відповідь:").pack(anchor="w")
            self.correct_entry = tb.Entry(self.dynamic_frame)
            self.correct_entry.pack(fill="x")

        elif q_type == "MultiChoice":
            tb.Label(self.dynamic_frame, text="Варіанти (з нового рядка):").pack(anchor="w")
            self.options_text = tb.Text(self.dynamic_frame, height=4)
            self.options_text.pack(fill="x", pady=(0, 10))
            tb.Label(self.dynamic_frame, text="Правильні відповіді (через кому):").pack(anchor="w")
            self.correct_entry = tb.Entry(self.dynamic_frame)
            self.correct_entry.pack(fill="x")

        elif q_type == "Text":
            tb.Label(self.dynamic_frame, text="Ключові слова (через кому):").pack(anchor="w")
            self.keywords_entry = tb.Entry(self.dynamic_frame)
            self.keywords_entry.pack(fill="x")

        elif q_type == "Scale":
            tb.Label(self.dynamic_frame, text="Правильне числове значення:").pack(anchor="w")
            self.val_entry = tb.Entry(self.dynamic_frame)
            self.val_entry.pack(fill="x", pady=(0, 10))
            tb.Label(self.dynamic_frame, text="Допустима похибка (наприклад, 1):").pack(anchor="w")
            self.tol_entry = tb.Entry(self.dynamic_frame)
            self.tol_entry.pack(fill="x")

        elif q_type == "TrueFalse":
            tb.Label(self.dynamic_frame, text="Правильна відповідь:").pack(anchor="w")
            self.tf_var = tb.StringVar(value="Правда")
            tb.Combobox(self.dynamic_frame, textvariable=self.tf_var, state="readonly",
                        values=["Правда", "Брехня"]).pack(fill="x")

        elif q_type == "Matching":
            tb.Label(self.dynamic_frame, text="Пари через тире 'Термін - Визначення' (з нового рядка):").pack(
                anchor="w")
            self.match_text = tb.Text(self.dynamic_frame, height=5)
            self.match_text.pack(fill="x")

        elif q_type == "Ordering":
            tb.Label(self.dynamic_frame, text="Правильна послідовність (кожен елемент з нового рядка):").pack(
                anchor="w")
            self.order_text = tb.Text(self.dynamic_frame, height=5)
            self.order_text.pack(fill="x")

        elif q_type == "FillBlank":
            tb.Label(self.dynamic_frame, text="Допустимі варіанти пропущеного слова (через кому):").pack(anchor="w")
            self.blank_entry = tb.Entry(self.dynamic_frame)
            self.blank_entry.pack(fill="x")

    def save_question(self):
        q_text = self.text_entry.get("1.0", "end").strip()
        if not q_text:
            messagebox.showwarning("Увага", "Введіть текст питання!")
            return

        difficulty = self.diff_var.get()
        q_type = self.type_var.get()
        new_q = None

        try:
            if q_type == "SingleChoice":
                options = [opt.strip() for opt in self.options_text.get("1.0", "end").strip().split('\n') if
                           opt.strip()]
                correct = self.correct_entry.get().strip()
                new_q = SingleChoiceQuestion(q_text, options, correct, difficulty)

            elif q_type == "MultiChoice":
                options = [opt.strip() for opt in self.options_text.get("1.0", "end").strip().split('\n') if
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

            elif q_type == "TrueFalse":
                correct_bool = True if self.tf_var.get() == "Правда" else False
                new_q = TrueFalseQuestion(q_text, correct_bool, difficulty)

            elif q_type == "Matching":
                lines = [line.strip() for line in self.match_text.get("1.0", "end").strip().split('\n') if line.strip()]
                pairs = {}
                for line in lines:
                    if '-' in line:
                        k, v = line.split('-', 1)
                        pairs[k.strip()] = v.strip()
                new_q = MatchingQuestion(q_text, pairs, difficulty)

            elif q_type == "Ordering":
                correct_order = [line.strip() for line in self.order_text.get("1.0", "end").strip().split('\n') if
                                 line.strip()]
                new_q = OrderingQuestion(q_text, correct_order, difficulty)

            elif q_type == "FillBlank":
                acceptable = [ans.strip() for ans in self.blank_entry.get().split(',') if ans.strip()]
                new_q = FillBlankQuestion(q_text, acceptable, difficulty)

            self.editor_app.tests[self.editor_app.current_test_name].append(new_q)
            self.editor_app.refresh_questions_list()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Помилка введення", f"Перевірте правильність заповнення полів!\nДеталі: {e}")


if __name__ == "__main__":
    root = tb.Window(themename="cosmo")
    app = TestEditorApp(root)
    root.mainloop()