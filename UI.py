import os
import tkinter as tk
from tkinter import filedialog, messagebox

_selected_file_path = None

def _choose_file():
    global _selected_file_path
    file_path = filedialog.askopenfilename(
        title="Выберите файл",
        filetypes=[
            ("CSV Файлы", "*.csv")
        ]
    )
    if file_path:
        _selected_file_path = file_path
        _label_file.config(text=f"Выбрано: {file_path.split('/')[-1]}")
        _btn_verify.config(state="normal")
    else:
        _selected_file_path = None
        _label_file.config(text="Файл не выбран")
        _btn_verify.config(state="disabled")

def _verify_sll():
    global _selected_file_path
    if _selected_file_path:
        from main import main_processing
        try:
            result = main_processing(_selected_file_path)
            messagebox.showinfo("Результат", f"Проверка завершена!\n{result}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    else:
        messagebox.showwarning("Ошибка", "Сначала выберите файл!")

_label_file = None
_btn_verify = None
_label_count = None
_counter_var = None
_root = None
_is_need_open = True

def build_ui():
    global _label_file, _btn_verify, _label_count, _counter_var, _root, _is_need_open

    _root = tk.Tk()
    _root.title("Проверка SLL")
    _root.geometry("400x150")
    _root.resizable(False, False)

    _label_file = tk.Label(_root, text="Файл не выбран", pady=10)
    _label_file.pack(side=tk.TOP)

    _is_need_open = tk.BooleanVar()
    _is_need_open.set(True)
    checkbox = tk.Checkbutton(_root, text="Открыть файл после окончания работы?", width=40, variable=_is_need_open)
    checkbox.pack(side=tk.RIGHT)

    btn_choose = tk.Button(_root, text="Выбрать файл", command=_choose_file, width=20)
    btn_choose.pack(pady=5 , side=tk.TOP)

    _btn_verify = tk.Button(_root, text="Сверить SLL", command=_verify_sll, width=20, state="disabled")
    _btn_verify.pack(pady=10, side=tk.TOP)

    _counter_var = tk.StringVar()
    _label_count = tk.Label(_root, textvariable=_counter_var, pady=10, padx= 10)
    _label_count.pack(side=tk.LEFT)

    _root.mainloop()

def change_progress_ui(size, last_processed):
    global _counter_var, _root
    _counter_var.set(f"{last_processed} / {size}")
    _root.update_idletasks()

def openOutputFile(output_file_path):
    global _is_need_open
    if _is_need_open:
        try:
            os.startfile(output_file_path)
        except FileNotFoundError:
            print(f"Файл не найден: {output_file_path}")
        except Exception as e:
            print(f"Ошибка при открытии файла: {e}")