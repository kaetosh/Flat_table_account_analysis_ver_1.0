import os
import time
import pandas as pd
from pyfiglet import Figlet

from dialog_user import select_folder
from logger import logger

from preprocessing_openpyxl import preprocessing_file_excel
from resaving_files import save_as_xlsx_not_alert

from analysis_deviations import revolutions_before_processing, revolutions_after_processing

from processing.A_table_header import table_header
from processing.B_handle_missing_values_in_account import handle_missing_values_in_account
from processing.C_horizontal_structure import horizontal_structure
from processing.D_corr_account_column import corr_account_col
from processing.E_lines_delete import lines_delete
from processing.F_shiftable_level import shiftable_level
from config import start_message
from utility_functions import delete_folders, terminate_script

f1 = Figlet(font='ansi_shadow', justify="center")
f2 = Figlet(font='ansi_shadow', justify="center")

print(f1.renderText("Flat analysis"), f2.renderText("of the 1C account"))
time.sleep(2)
print(start_message)
logger.info(f"Сейчас будет предложено выбрать папку с файлами Excel - анализами счетов.")
time.sleep(2)
select_folder()
from config import folder_path_converted, folder_path

logger.info(f"Выбрана папка {folder_path}, проверим наличие файлов Excel...")

save_as_xlsx_not_alert()
files = os.listdir(folder_path_converted)
excel_files = [file for file in files if file.endswith('.xlsx') or file.endswith('.xls')]
if not excel_files:
    terminate_script(f'Не найдены файлы Excel в папке {folder_path_converted}. Скрипт завершен неудачно')

# Инициализируем пустой словарь, куда мы добавим обработанные таблицы каждой компании, затем объединим эти файлы в один.
dict_df = {} # для обрабатываемых таблиц
dict_df_check = {} # для таблиц сверки оборотов до и после обработки


def main_process():
    empty_files = []

    for file_excel in excel_files:
        # предварительная обработка с помощью openpyxl (снятие объединения, уровни)

        folder_path_converted_file = os.path.normpath(os.path.join(folder_path_converted, file_excel))
        #file_excel_treatment = preprocessing_file_excel(f'{folder_path_converted}\{file_excel}')

        file_excel_treatment = preprocessing_file_excel(folder_path_converted_file)

        # загрузка в pandas
        df = pd.read_excel(file_excel_treatment)
        logger.info(f'{file_excel}: успешно загрузили в DataFrame')

        # устанавливаем шапку таблицы
        table_header(df, file_excel)
        logger.info(f'{file_excel}: успешно создали шапку таблицы')

        # если есть незаполненные поля группировки (вид номенклатуры например), ставим "не_заполнено"
        if handle_missing_values_in_account(df):
            logger.info(f'{file_excel}: обнаружили незаполненные поля, там проставили "не заполнено"')

        # разносим иерархию в горизонтальную плоскость
        # если иерархии нет, то файл пустой, пропускаем его
        if horizontal_structure(df, file_excel):
            logger.info(f'{file_excel}: пустой, пропускаем его')
            empty_files.append(f'{file_excel}')
            continue
        else:
            logger.info(f'{file_excel}: разнесли иерархию в горизонтальную плоскость')

        # Добавляем столбец с корр счетом
        ns = corr_account_col(df, file_excel)
        logger.info(f'{file_excel}: добавили столбец с корр счетом')

        # формируем вспомогательную таблицу с оборотами до обработки
        # потом сравним данные с итоговой таблицей, чтобы убедиться в правильности результата
        df_for_check = revolutions_before_processing(df, file_excel, ns.sign_1c, ns.debet_name, ns.credit_name)
        logger.info(f'{file_excel}: сформировали вспомогательную таблицу с оборотами до обработки')
        if df_for_check.empty:
            logger.info(f'{file_excel}: пустой, пропускаем его')
            empty_files.append(f'{file_excel}')
            continue

        # удаляем дублирующие строки (родительские счета, счета по которым есть аналитика, обороты, сальдо и т.д.)
        df = lines_delete(df, ns.sign_1c, file_excel)
        logger.info(f'{file_excel}: удалили дублирующие строки')
        
        # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
        shiftable_level(df)
        logger.info(f'{file_excel}: сдвинули столбцы, чтобы субсчета располагались в одном столбце')

        # формируем вспомогательную таблицу с оборотами после обработки
        # записываем данные по отклонениям до/после обработки
        df_check = revolutions_after_processing(df, df_for_check, file_excel)
        dict_df_check[file_excel] = df_check
        logger.info(f'{file_excel}: сформировали вспомогательную таблицу с оборотами после обработки')

        # запишем таблицу в словарь
        dict_df[file_excel] = df
        logger.info(f'{file_excel}: успешно записали таблицу в словарь для дальнейшего объединения с другими таблицами')

    # объединяем все таблицы в одну
    result, result_check = None, None
    try:
        result = pd.concat(list(dict_df.values()))
        logger.info('объединили все таблицы в одну')
        
        # Повторно сдвиг столбцов, чтобы субсчета располагались в одном столбце
        shiftable_level(result)
        logger.info('повторно сдвинули столбцы уже в сводной таблице, чтобы субсчета располагались в одном столбце')
        
        result_check = pd.concat(list(dict_df_check.values()))
        logger.info('объединили все таблицы с проверкой оборотов в одну')
        
        deviation_rpm = (result_check['Разница_С_кред'] + result_check['Разница_В_дебет']).sum()
        if deviation_rpm < 1:
            logger.info('отклонения по оборотам до и после обработки менее 1')
        else:
            logger.warning('обнаружены существенные отклонения по оборотам до и после обработки. См "СВОД_ОТКЛ_анализ_счетов.xlsx"')
        
        logger.info('Объединение завершено, пытаемся выгрузить файл в excel...')
    except Exception as e:
        terminate_script(f'Ошибка при объединении файлов {e}')

    # выгружаем в excel
    try:
        folder_path_summary_files = os.path.join(folder_path, "_СВОД_анализ_счетов.xlsx")

        with pd.ExcelWriter(folder_path_summary_files) as writer:
            result.to_excel(writer, sheet_name='Свод', index=False)
            result_check.to_excel(writer, sheet_name='Сверка', index=False)
        logger.info('Файл успешно выгружен в excel')

    except Exception as e:
        terminate_script(f'Ошибка при сохранении файла в excel: {e}')

    delete_folders()
    
    if empty_files:
        logger.info(f'Анализы счетов без оборотов ({len(empty_files)}): {empty_files}')
    
    logger.info('Скрипт завершен успешно. Можно закрыть программу.')

    

if __name__ == "__main__":
    main_process()
    input()
