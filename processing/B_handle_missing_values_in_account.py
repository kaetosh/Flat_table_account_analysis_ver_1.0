"""
Найдем пустые значения в столбце Счет (не заполненные поля Вид субконто или субконто),
чтобы в дальнейшем поставить признак "Не заполнено"
"""

import numpy as np
from logger import logger
import pandas as pd
from utility_functions import is_accounting_code


def handle_missing_values_in_account(df, file_excel):
    result = False
    current_ind = None
    # Приводим значения столбца Счет к числовому, в т.ч. и NaN
    # (получим np.nan, чтобы работал метод ffill), строковые не трогаем
    
    
    
    df['Счет'] = df['Счет'].apply(lambda x: pd.to_numeric(x) if not isinstance(x, str) else x)
    
   
    
    # проходим по значениям столбца Счет
    for index, value in df['Счет'].items():
        # Если значение float (точнее np.nan), т.е. пустое или счет бухучета
        if isinstance(value, float) or is_accounting_code(value):
            current_ind = index  # запоминаем индекс этого значения
        else:
            try:
                # иначе если значение float (точнее np.nan), т.е пустое
                if isinstance(df.loc[current_ind, 'Счет'], float):
                    break  # выходим из цикла
            except KeyError:
                #logger.error(f'ERROR: {current_ind}')
                continue
            else:
                current_ind = index  # иначе запоминаем индекс этого значения

    # если найдено пустое значение
    if current_ind and (isinstance(df.loc[current_ind, 'Счет'], float)):
        df.loc[current_ind, 'Счет'] = 'Не_указано'  # заполняем его как Не_заполнено
        level_empty_value = df.loc[current_ind, 'Уровень']  # получим уровень этой строки (где пустое значение)
        # проверим все строки данного уровня, если они не заполнены, ставим в них Не_заполнено
        df.loc[:, 'Счет'] = np.where((df['Уровень'] == level_empty_value)
                                     & (df['Счет'].isna()), 'Не_указано', df['Счет'])
        result = True
    logger.info(f'{file_excel}: добавили столбец с наименованием файла (для различения наименований компаний)')
    
    
    
    df['Счет'] = df['Счет'].ffill()  # пустые значения в данном столбце заполнили последними непустыми значениями
    df['Счет'] = df['Счет'].apply(lambda x: str(x))
    df['Счет'] = df['Счет'].apply(lambda x: f'0{x}' if (len(str(x)) == 1 and is_accounting_code(x)) else x)
    

    
    return result
