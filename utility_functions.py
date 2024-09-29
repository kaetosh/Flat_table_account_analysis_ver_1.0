import os
import shutil
import sys
import functools
import time

import config
from logger import logger

# определяет, является ли значение бухгалтерским счетом
def is_accounting_code(value):
    if value:
        try:
            parts = str(value).split('.')
            has_digit = any(part.isdigit() for part in parts)
            # Checking whether each part consists only of numbers (with a length of 1 or 2) or (if the length is less than 3) only of letters
            return has_digit and all((part.isdigit() and len(part) <= 2) or (len(part) < 3 and part.isalpha()) for part in parts)
        except TypeError:
            return False
    else:
        return False

# в случае ошибки - удаление временных папок и файлов
def terminate_script(error_message: str):
    """
    Terminates the script with an error message and deletes temporary folders.
    """
    sys.stdout.write('\r' + ' ' * config.count_clean_simb)  # очистка предыдущего символа крутилки
    sys.stdout.flush()
    logger.error(error_message)
    delete_folders()
    sys.stdout.write('\r' + ' ' * config.count_clean_simb)  # очистка предыдущего символа крутилки
    sys.stdout.flush()
    logger.info("Скрипт завершен безуспешно. Можно закрыть программу. ")
    input()
    sys.exit()

# удаление временных папок
def delete_folders():
    """
    Deletes temporary folders.
    """
    for dir_ in [config.folder_path_preprocessing, config.folder_path_converted]:
        if os.path.exists(dir_):
            try:
                shutil.rmtree(dir_)
                logger_with_spinner(f"Папка и ее содержимое {dir_} были успешно удалены.")
            except OSError as e:
                logger_with_spinner(f"Error: {e.filename} - {e.strerror}", warning_log=True)
        else:
            logger_with_spinner(f"Папка {dir_} не существует.", warning_log=True)

# декоратор к функциям обработки файлов Excel (на каждом этапе A, B, C,...)
# отлавливающий ошибку, чтобы корректно завершить программу и удалить временные папки
def catch_errors():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                terminate_script(f'{e}')
        return wrapper
    return decorator

# индикатор работы программы
def spinner():
    symbols = ['(-.-)Zz', '(-.o)  ', '(o.o)  ', '(O.o)  ', '(O.O)  ', '(o.O)  ', '(o.o)  ', '(-.-)zZ', '(-.-)Zz',
               '(-.-)zZ']
    while True:
        for symbol in symbols:
            sys.stdout.write('\r' + symbol)
            sys.stdout.flush()
            time.sleep(0.45)

# вспомогательная функция, которая позволяет индикатору работы программы всегда находиться
# внизу консоли, после вывода print
def print_with_spinner(*text_for_print):
    sys.stdout.write('\r' + ' ' * config.count_clean_simb)  # очистка предыдущего символа крутилки
    sys.stdout.flush()
    for i in text_for_print:
        print(i)

# вспомогательная функция, которая позволяет индикатору работы программы всегда находиться
# внизу консоли, после вывода logger
def logger_with_spinner(text_log, warning_log=False):
    sys.stdout.write('\r' + ' ' * config.count_clean_simb)  # очистка предыдущего символа крутилки
    sys.stdout.flush()
    if warning_log:
        logger.warning(text_log)
    else:
        logger.info(text_log)