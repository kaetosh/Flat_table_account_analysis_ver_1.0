"""
Найдем пустые значения в столбце Счет (не заполненные поля Вид субконто или субконто),
чтобы в дальнейшем поставить признак "Не заполнено"
"""

import numpy as np

from config import exclude_values
from utility_functions import is_accounting_code, catch_errors


@catch_errors()
def handle_missing_values_in_account(df):
    result = False
    # Приводим значения столбца Счет к числовому, в т.ч. и NaN
    # (получим np.nan, чтобы работал метод ffill), строковые не трогаем

    try:
        mask = df['Счет'].isna() & ~df['Кор.счет'].apply(is_accounting_code) & df['Кор.счет'].isin(exclude_values)
    except KeyError:
        mask = df['Счет'].isna() & ~df['Кор. Счет'].apply(is_accounting_code) & df['Кор. Счет'].isin(exclude_values)
    df['Счет'] = np.where(mask, 'Не_заполнено', df['Счет'])
    
    df['Счет'] = df['Счет'].ffill()  # пустые значения в данном столбце заполнили последними непустыми значениями
    df['Счет'] = df['Счет'].apply(lambda x: str(x))
    df['Счет'] = df['Счет'].apply(lambda x: f'0{x}' if (len(str(x)) == 1 and is_accounting_code(x)) else x)

    return result
