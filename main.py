import os
import sys
import pandas as pd

from analysis_deviations import revolutions_before_processing, revolutions_after_processing
from logger import logger
from processing.C_horizontal_structure import horizontal_structure
from processing.E_corr_account_column import corr_account_col
from processing.F_lines_delete import lines_delete
from processing.G_shiftable_level import shiftable_level
from settings import folder_path
from preprocessing_openpyxl import preprocessing_file_excel
from processing.A_table_header import table_header
from processing.B_handle_missing_values_in_account import handle_missing_values_in_account


pd.set_option('display.max_columns', None)

files = os.listdir(folder_path)
excel_files = [file for file in files if file.endswith('.xlsx') or file.endswith('.xls')]
if not excel_files:
    logger.error(f'Не найдены файлы Excel в папке {folder_path}')
    sys.exit()

# Инициализируем пустой словарь, куда мы добавим обработанные таблицы каждой компании, затем объединим эти файлы в один.

dict_df = {}
dict_df_check = {}


def main_process():
    for file_excel in excel_files:
        # предварительная обработка с помощью openpyxl (снятие объединения, уровни)
        file_excel_treatment = preprocessing_file_excel(f'{folder_path}/{file_excel}')

        # загрузка в pandas
        df = pd.read_excel(file_excel_treatment)
        logger.info(f'{file_excel}: успешно загрузили в DataFrame')

        # устанавливаем шапку таблицы
        table_header(df, file_excel)

        # если есть незаполненные поля группировки (вид номенклатуры например), ставим "не_заполнено"
        handle_missing_values_in_account(df, file_excel)

        # разносим иерархию в горизонтальную плоскость
        # если иерархии нет, то файл пустой, пропускаем его
        if horizontal_structure(df, file_excel):
            continue

        # Добавляем столбец с корр счетом
        ns = corr_account_col(df, file_excel)

        # формируем вспомогательную таблицу с оборотами до обработки
        # потом сравним данные с итоговой таблицей, чтобы убедиться в правильности результата
        df_for_check = revolutions_before_processing(df, file_excel, ns.sign_1c, ns.debet_name, ns.credit_name)

        # удаляем дублирующие строки (родительские счета, счета по которым есть аналитика, обороты, сальдо и т.д.)
        df = lines_delete(df, ns.sign_1c, file_excel, ns.debet_name, ns.credit_name)

        # Сдвиг столбцов, чтобы субсчета располагались в одном столбце
        shiftable_level(df)

        # формируем вспомогательную таблицу с оборотами после обработки
        # записываем данные по отклонениям до/после обработки
        df_check = revolutions_after_processing(df, df_for_check, file_excel)
        dict_df_check[file_excel] = df_check

        # запишем таблицу в словарь
        dict_df[file_excel] = df
        logger.info(f'{file_excel}: успешно записали таблицу в словарь для дальнейшего объединения с другими таблицами')

    # объединяем все таблицы в одну
    result, result_check = None, None
    try:
        result = pd.concat(list(dict_df.values()))
        result_check = pd.concat(list(dict_df_check.values()))
        logger.info('\nОбъединение завершено, пытаемся выгрузить файл в excel...')
    except Exception as e:
        logger.error(f'\n\nОшибка при объединении файлов {e}')
        # Ошибка при объединении файлов could not convert string to float: 'Исх.файл'
    # выгружаем в excel
    try:
        result.to_excel('summary_files/СВОД_анализ_счетов.xlsx', index=False)
        result_check.to_excel('summary_files/СВОД_ОТКЛ_анализ_счетов.xlsx', index=False)
        logger.info('\nФайл успешно выгружен в excel, скрипт завершен!')
    except Exception as e:
        logger.error(f'\nОшибка при сохранении файла в excel: {e}')


if __name__ == "__main__":
    main_process()
