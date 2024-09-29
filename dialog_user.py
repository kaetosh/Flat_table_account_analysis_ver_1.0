import os
import tkinter as tk
from tkinter import filedialog
import sys

import config
from utility_functions import logger_with_spinner

# выбор папки с обрабатываемыми файлами
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    folder_path = filedialog.askdirectory()  # Открыть диалог выбора папки
    if not folder_path:
        logger_with_spinner("Отмена выбора папки. Скрипт завершен неудачно.")
        sys.exit()  # Завершить работу скрипта, если выбор папки отменен
    config.folder_path = os.path.normpath(folder_path)
    config.folder_path_converted = os.path.normpath(os.path.join(folder_path, "ConvertedFiles"))
    config.folder_path_preprocessing = os.path.normpath(os.path.join(folder_path, "preprocessing_files"))

