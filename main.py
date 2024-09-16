import os
import shutil
import sys
import pandas as pd
from pyfiglet import Figlet

from dialog_user import select_folder
from logger import logger

from preprocessing_openpyxl import preprocessing_file_excel
from resaving_files import save_as_xlsx_not_alert

from analysis_deviations import revolutions_before_processing, revolutions_after_processing
#https://disk.yandex.ru/d/Xe0MNB-CnPXDaA

from processing.A_table_header import table_header
from processing.B_handle_missing_values_in_account import handle_missing_values_in_account
from processing.C_horizontal_structure import horizontal_structure
from processing.E_corr_account_column import corr_account_col
from processing.F_lines_delete import lines_delete
from processing.G_shiftable_level import shiftable_level


f1 = Figlet(font='ansi_shadow', justify="center")
f2 = Figlet(font='ansi_shadow', justify="center")
f3 = Figlet(font='soft', justify="center")

print(f1.renderText("Flat table"), f2.renderText("account analysis"), f3.renderText("ver 1.0"))

folder_path = select_folder()
save_as_xlsx_not_alert(folder_path)
folder_path = os.path.normpath(folder_path)
folder_path_converted = os.path.join(folder_path, "ConvertedFiles")
files = os.listdir(folder_path_converted)
excel_files = [file for file in files if file.endswith('.xlsx') or file.endswith('.xls')]
if not excel_files:
    logger.error(f'Не найдены файлы Excel в папке {folder_path_converted}')
    print(f'Не найдены файлы Excel в папке {folder_path_converted}')
    sys.exit()

# Инициализируем пустой словарь, куда мы добавим обработанные таблицы каждой компании, затем объединим эти файлы в один.
dict_df = {} # для обрабатываемых таблиц
dict_df_check = {} # для таблиц сверки оборотов до и после обработки


def main_process():
    empty_files = []

       
    for file_excel in excel_files:
        # предварительная обработка с помощью openpyxl (снятие объединения, уровни)
        file_excel_treatment = preprocessing_file_excel(f'{folder_path_converted}/{file_excel}')

        # загрузка в pandas
        df = pd.read_excel(file_excel_treatment)
        logger.info(f'{file_excel}: успешно загрузили в DataFrame')
        print(f'{file_excel}: успешно загрузили в DataFrame')

        # устанавливаем шапку таблицы
        table_header(df, file_excel)
        print(f'{file_excel}: успешно создали шапку таблицы')

        # если есть незаполненные поля группировки (вид номенклатуры например), ставим "не_заполнено"
        if handle_missing_values_in_account(df, file_excel):
            print(f'{file_excel}: обнаружили незаполненные поля, там проставили "не заполнено"')
        

        # разносим иерархию в горизонтальную плоскость
        # если иерархии нет, то файл пустой, пропускаем его
        if horizontal_structure(df, file_excel):
            print(f'{file_excel}: пустой, пропускаем его')
            empty_files.append(f'{file_excel}')
            continue
        else:
            print(f'{file_excel}: разнесли иерархию в горизонтальную плоскость')

        # Добавляем столбец с корр счетом
        ns = corr_account_col(df, file_excel)
        print(f'{file_excel}: добавили столбец с корр счетом')

        # формируем вспомогательную таблицу с оборотами до обработки
        # потом сравним данные с итоговой таблицей, чтобы убедиться в правильности результата
        df_for_check = revolutions_before_processing(df, file_excel, ns.sign_1c, ns.debet_name, ns.credit_name)
        print(f'{file_excel}: сформировали вспомогательную таблицу с оборотами до обработки')
        if df_for_check.empty:
            print(f'{file_excel}: пустой, пропускаем его')
            empty_files.append(f'{file_excel}')
            continue

        # удаляем дублирующие строки (родительские счета, счета по которым есть аналитика, обороты, сальдо и т.д.)
        df = lines_delete(df, ns.sign_1c, file_excel)
        print(f'{file_excel}: удалили дублирующие строки')
        
        # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
        shiftable_level(df)
        print(f'{file_excel}: сдвинули столбцы, чтобы субсчета располагались в одном столбце')

        # формируем вспомогательную таблицу с оборотами после обработки
        # записываем данные по отклонениям до/после обработки
        df_check = revolutions_after_processing(df, df_for_check, file_excel)
        dict_df_check[file_excel] = df_check
        print(f'{file_excel}: сформировали вспомогательную таблицу с оборотами после обработки')

        # запишем таблицу в словарь
        dict_df[file_excel] = df
        logger.info(f'{file_excel}: успешно записали таблицу в словарь для дальнейшего объединения с другими таблицами')
        print(f'{file_excel}: успешно записали таблицу в словарь для дальнейшего объединения с другими таблицами\n')

    # объединяем все таблицы в одну
    result, result_check = None, None
    try:
        result = pd.concat(list(dict_df.values()))
        print('объединили все таблицы в одну')
        
        # Повторно сдвиг столбцов, чтобы субсчета располагались в одном столбце
        shiftable_level(result)
        print('повторно сдвинули столбцы уже в сводной таблице, чтобы субсчета располагались в одном столбце')
        
        result_check = pd.concat(list(dict_df_check.values()))
        print('объединили все таблицы с проверкой оборотов в одну')
        
        deviation_rpm = (result_check['Разница_С_кред'] + result_check['Разница_В_дебет']).sum()
        if deviation_rpm < 1:
            logger.info('\nотклонения по оборотам до и после обработки менее 1')
            print('\nотклонения по оборотам до и после обработки менее 1')
        else:
            logger.error('\nобнаружены существенные отклонения по оборотам до и после обработки. См "СВОД_ОТКЛ_анализ_счетов.xlsx"')
            print('\nобнаружены существенные отклонения по оборотам до и после обработки. См "СВОД_ОТКЛ_анализ_счетов.xlsx"')
        
        logger.info('\nОбъединение завершено, пытаемся выгрузить файл в excel...')
        print('\nОбъединение завершено, пытаемся выгрузить файл в excel...')
    except Exception as e:
        print(f'\n\nОшибка при объединении файлов {e}')
        logger.error(f'\n\nОшибка при объединении файлов {e}')
    # выгружаем в excel
    try:
        summary_folder = os.path.join(folder_path, "summary_files")
        folder_path_summary_files = os.path.join(summary_folder, "СВОД_анализ_счетов.xlsx")
        #folder_path_summary_files = os.path.join(folder_path, "summary_files/СВОД_анализ_счетов.xlsx")
        if not os.path.exists(summary_folder):
            os.makedirs(summary_folder)
        result.to_excel(folder_path_summary_files, index=False)
        folder_path_result_check = os.path.join(folder_path, "summary_files/СВОД_ОТКЛ_анализ_счетов.xlsx")
        result_check.to_excel(folder_path_result_check, index=False)
        logger.info('\nФайл успешно выгружен в excel')
        print('\nФайл успешно выгружен в excel')
    except Exception as e:
        print(f'\nОшибка при сохранении файла в excel: {e}')
        logger.error(f'\nОшибка при сохранении файла в excel: {e}')

    folder_path_del_files = 'preprocessing_files'

    # Убедитесь, что папка существует перед ее удалением
    if os.path.exists(folder_path_del_files):
        # Удаляем файлы из папки
        for filename in os.listdir(folder_path_del_files):
            file_path = os.path.join(folder_path_del_files, filename)
            # Удаляем файл
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Удаляем папку
        shutil.rmtree(folder_path_del_files)
        print(f"Папка и ее содержимое {folder_path_del_files} были успешно удалены.")
    else:
        print(f"Папка {folder_path_del_files} не существует.")
    
    for filename in os.listdir(folder_path_converted):
        file_path = os.path.join(folder_path_converted, filename)
        os.remove(file_path)
    
    try:
        os.rmdir(folder_path_converted)
        print('Удалены временные файлы')
        logger.info('Удалены временные файлы')
    except OSError as e:
        logger.info(f"Error: {e.filename} - {e.strerror}")
        print(f"Error: {e.filename} - {e.strerror}")
    
    if empty_files:
        logger.info(f'Анализы счетов без оборотов ({len(empty_files)}): {empty_files}')
        print(f'Анализы счетов без оборотов ({len(empty_files)}): {empty_files}')
    
    logger.info('Скрипт завершен!!!')
    print('Скрипт завершен!!!')

    
    

if __name__ == "__main__":
    main_process()
    print("Нажмите Enter для выхода.")
    input()
