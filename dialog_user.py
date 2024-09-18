import tkinter as tk
from tkinter import filedialog
import sys

from logger import logger

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    folder_path = filedialog.askdirectory()  # Открыть диалог выбора папки
    if not folder_path:
        logger.info("Отмена выбора папки. Скрипт завершен неудачно.")
        sys.exit()  # Завершить работу скрипта, если выбор папки отменен
    return folder_path

