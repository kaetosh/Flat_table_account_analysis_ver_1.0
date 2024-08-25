import os
import sys
import pandas as pd

from analysis_deviations import revolutions_before_processing
from logger import logger
from processing.C_horizontal_structure import horizontal_structure
from processing.E_corr_account_column import corr_account_col
from processing.F_lines_delete import lines_delete
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
        df_for_check.to_excel('check.xlsx')

        lines_delete(df, ns.sign_1c)

        df.to_excel('final.xlsx')


if __name__ == "__main__":
    main_process()
