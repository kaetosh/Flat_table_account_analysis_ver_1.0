import tkinter as tk
from tkinter import filedialog

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    folder_path = filedialog.askdirectory()  # Открыть диалог выбора папки
    return folder_path