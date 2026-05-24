import ttkbootstrap as tb
from ttkbootstrap.constants import *
import subprocess
import sys

def open_admin():
    subprocess.Popen([sys.executable, "editor_module.py"])

def open_student():
    subprocess.Popen([sys.executable, "test_module.py"])

root = tb.Window(themename="cosmo")
root.title("Стартове меню")
root.geometry("500x350")
root.eval('tk::PlaceWindow . center')

tb.Label(root, text="Система Тестування", font=("Helvetica", 22, "bold"), bootstyle=PRIMARY).pack(pady=40)
tb.Label(root, text="Оберіть режим роботи:", font=("Helvetica", 14), bootstyle=SECONDARY).pack(pady=10)

btn_frame = tb.Frame(root)
btn_frame.pack(fill="x", padx=50)

tb.Button(btn_frame, text="Створити тест", bootstyle=(SUCCESS, OUTLINE),
          width=30, command=open_admin).pack(pady=10, ipady=5)

tb.Button(btn_frame, text="Тестування", bootstyle=(INFO, OUTLINE),
          width=30, command=open_student).pack(pady=10, ipady=5)

root.mainloop()