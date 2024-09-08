import types
from logger import logger

from utility_functions import is_accounting_code


def corr_account_col(df, file_excel):
    # Добавление нового столбца
    sign_1c = 'Кор.счет'  # предположим, что файл - выгрузка из серой 1с
    debet_name = 'С кред. счетов'
    credit_name = 'В дебет счетов'

    if 'Дебет' in df.columns.to_list():  # однако столбец "Дебет" встречается в желтой 1С, а не серой
        sign_1c = 'Кор. Счет'  # тогда обрабатываем как файл из желтой 1С
        debet_name = 'Дебет'
        credit_name = 'Кредит'
    # добавим столбец корр.счет, взяв его из основного столбца, при условии, что значение - бухгалтерских счет (функция is_accounting_code)
    df['Корр_счет'] = df[sign_1c].apply(lambda x: str(x) if (is_accounting_code(x) or str(x) == '0') else None)
    
    
    
    
    
    
    # добавим нолик, если счет до 10, чтобы было 01 02 04 05 07 08 09
    df['Корр_счет'] = df['Корр_счет'].apply(lambda x: f'0{x}' if len(str(x)) == 1 else x)
    
    
    # добавим нолик к счетам и в основном столбце
    df[sign_1c] = df[sign_1c].apply(lambda x: f'0{x}' if len(str(x)) == 1 else x)

    # Заполнение пропущенных значений в столбце значениями из предыдущей строки
    df['Корр_счет'] = df['Корр_счет'].ffill()
    logger.info(f'{file_excel}: добавили столбец с корр.счетом')


    ns = types.SimpleNamespace(**locals())
    return ns
