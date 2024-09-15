# # -*- coding: utf-8 -*-
# """
# Created on Wed Aug 28 16:36:46 2024
#
# @author: a.karabedyan
# """

import os
import win32com.client

from logger import logger
#from settings import folder_path

def save_as_xlsx_not_alert(folder_path):

    # Нормализуем путь
    folder_path = os.path.normpath(folder_path)
    sNewFolderPath = os.path.join(folder_path, "ConvertedFiles")
    
    if not os.path.exists(sNewFolderPath):
        os.makedirs(sNewFolderPath)

    # Итерируемся по всем файлам в выбранной папке
    for oFile in os.listdir(folder_path):
        # Проверяем, является ли файл Excel файлом
        if oFile.endswith(('.xls', '.xlsx')):
            # Полный путь к файлу
            file_path = os.path.join(folder_path, oFile)
            
            # Проверка на существование файла
            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                continue
            
            try:
                # Открываем Excel файл
                excel = win32com.client.Dispatch('Excel.Application')
                excel.Visible = False  # Скрыть приложение Excel
                excel.DisplayAlerts = False  # Отключить предупреждения

                wb = excel.Workbooks.Open(file_path)

                # Сохраняем файл как xlsx
                new_file_path = os.path.join(sNewFolderPath, os.path.splitext(oFile)[0] + '.xlsx')
                wb.SaveAs(new_file_path, FileFormat=51)

                # Закрываем книгу без сохранения изменений
                wb.Close(SaveChanges=False)
                logger.info(f'Исходный файл {oFile} пересохранен.')
                print(f'Исходный файл {oFile} пересохранен.')

            except Exception as e:
                print(f"Ошибка при обработке файла {oFile}: {e}")
                logger.error(f"Ошибка при обработке файла {oFile}: {e}")

            finally:
                # Убедитесь, что Excel будет закрыт
                excel.Quit()

    # Отображаем сообщение
    logger.info('Исходные файлы Excel пересохранены.')
    print('Все исходные файлы Excel пересохранены.')

