from logger import logger

from utility_functions import is_accounting_code


def revolutions_before_processing(df, file_excel, sign_1c, debet_name, credit_name):
    df_for_check = df[[sign_1c, debet_name, credit_name]].copy()
    df_for_check['Кор.счет_ЧЕК'] = df_for_check[sign_1c].apply(lambda x: x if is_accounting_code(x) else None).copy()
    df_for_check = df_for_check.dropna(subset=['Кор.счет_ЧЕК'])
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].fillna('')
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].astype(str)
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].apply(lambda x: f'0{x}' if len(x) == 1 else x)
    df_for_check = df_for_check[df_for_check['Кор.счет_ЧЕК'].str.match(r'^\d{2}$')].copy()
    df_for_check = df_for_check.groupby('Кор.счет_ЧЕК')[[debet_name, credit_name]].sum().copy()
    df_for_check = df_for_check.reset_index()
    if sign_1c != 'Кор.счет':
        df_for_check.rename(columns={'Дебет': 'С кред. счетов', 'Кредит': 'В дебет счетов'}, inplace=True)
    logger.info(f'{file_excel}: сформировали таблицу с оборотами в разрезе счетов до обработки')
    return df_for_check