# A function for determining whether a value is an accounting
import os
import shutil
import sys
import functools

import config
from logger import logger


def is_accounting_code(value):
    if value:
        try:
            parts = str(value).split('.')
            has_digit = any(part.isdigit() for part in parts)
            # Checking whether each part consists only of numbers or (if the length is less than 3) only of letters
            return has_digit and all(part.isdigit() or (len(part) < 3 and part.isalpha()) for part in parts)
        except TypeError:
            return False
    else:
        return False

def terminate_script(error_message: str):
    """
    Terminates the script with an error message and deletes temporary folders.
    """
    logger.error(error_message)
    delete_folders()
    logger.info("Скрипт завершен безуспешно. Можно закрыть программу. ")
    input()
    sys.exit()

def delete_folders():
    """
    Deletes temporary folders.
    """
    for dir_ in [config.folder_path_preprocessing, config.folder_path_converted]:
        if os.path.exists(dir_):
            try:
                shutil.rmtree(dir_)
                logger.info(f"Папка и ее содержимое {dir_} были успешно удалены.")
            except OSError as e:
                logger.error(f"Error: {e.filename} - {e.strerror}")
        else:
            logger.warning(f"Папка {dir_} не существует.")

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

