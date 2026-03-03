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

INCLUDE_WARNING = True
INCLUDE_ERROR = True
INCLUDE_SUCCESS = False

def build_ui():
    global _label_file, _btn_verify, _label_count, _counter_var, _root, _is_need_open, INCLUDE_WARNING, INCLUDE_ERROR, INCLUDE_SUCCESS

    _root = tk.Tk()
    _root.title("Проверка SLL")
    _root.geometry("400x300")
    _root.resizable(False, False)
    #####
    f_main = tk.Frame(_root)

    _label_file = tk.Label(f_main, text="Файл не выбран", pady=10)
    _label_file.pack(side=tk.TOP)

    btn_choose = tk.Button(f_main, text="Выбрать файл", command=_choose_file, width=20)
    btn_choose.pack(pady=5 , side=tk.TOP)

    f_main.pack()
    ####
    f_settings = tk.Frame(_root)

    text = tk.Label(f_settings, text="")
    text.pack(side=tk.TOP)

    _is_need_open = tk.BooleanVar()
    _is_need_open.set(True)
    checkbox_open = tk.Checkbutton(f_settings, text="Открыть файл после окончания работы?", width=40, variable=_is_need_open)
    checkbox_open.pack(side=tk.TOP)

    text = tk.Label(f_settings, text="")
    text.pack(side=tk.TOP)
    f_settings.pack()

    #### OWNER & ADMIN SETTINGS ####
    f_OWAD = tk.Frame(_root)


    text = tk.Label(f_OWAD, text="Отчеты по Владельцам\Админам")
    text.pack(side=tk.TOP)

    INCLUDE_ERROR = tk.BooleanVar()
    INCLUDE_ERROR.set(True)
    checkbox_error = tk.Checkbutton(f_OWAD, text="Включить в отчет: ERROR?", width=40, variable=INCLUDE_ERROR)
    checkbox_error.pack(side=tk.TOP)

    INCLUDE_WARNING = tk.BooleanVar()
    INCLUDE_WARNING.set(True)
    checkbox_warning = tk.Checkbutton(f_OWAD, text="Включить в отчет: WARNING?", width=40, variable=INCLUDE_WARNING)
    checkbox_warning.pack(side=tk.TOP)

    INCLUDE_SUCCESS = tk.BooleanVar()
    INCLUDE_SUCCESS.set(False)
    checkbox_success = tk.Checkbutton(f_OWAD, text="Включить в отчет: SUCCESS?", width=40, variable=INCLUDE_SUCCESS)
    checkbox_success.pack(side=tk.TOP)

    f_OWAD.pack()
    #### OWNER & ADMIN SETTINGS ####

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
    if _is_need_open.get():
        try:
            os.startfile(output_file_path)
        except FileNotFoundError:
            print(f"Файл не найден: {output_file_path}")
        except Exception as e:
            print(f"Ошибка при открытии файла: {e}")

def get_include_warning():
    global INCLUDE_WARNING
    return INCLUDE_WARNING.get()

def get_include_Error():
    global INCLUDE_ERROR
    return INCLUDE_ERROR.get()

def get_include_Success():
    global INCLUDE_SUCCESS
    return INCLUDE_SUCCESS.get()