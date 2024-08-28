from logger import logger
from settings import exclude_values
from utility_functions import is_accounting_code


# определяет родительские счета
def get_parent_accounts(account):
    parent_accounts = []
    for i in range(1, account.count('.') + 1):
        parent = '.'.join(account.split('.')[:-i])
        if parent not in parent_accounts:
            parent_accounts.append(parent)
    return parent_accounts

# определяет счета, у которых нет субсчетов
def accounting_code_without_subaccount(accounting_codes):
    accounting_codes_xx = [i[:2] for i in accounting_codes]
    count_dict = {}
    for item in accounting_codes_xx:
        if item in count_dict:
            count_dict[item] += 1
        else:
            count_dict[item] = 1
    result = [key for key, value in count_dict.items() if value == 1]
    result.append('00')
    result.append('000')
    return result

# Функция для проверки того, является ли счет без субсчетов
def is_parent(account, accounts):
    for acc in accounts:
        if acc.startswith(account + '.') and acc != account:
            return True
    return False

def lines_delete(df, sign_1c, file_excel, debet_name, credit_name):
    df_delete = df[~df[sign_1c].isin(exclude_values)]
    df_delete = df_delete.dropna(subset=[sign_1c]).copy()
    df_delete = df_delete[df_delete['Курсив'] == 0][[sign_1c, 'Корр_счет']]
    unique_df = df_delete.drop_duplicates(subset=[sign_1c, 'Корр_счет'])
    unique_df = unique_df[~unique_df['Корр_счет'].isin([None])]

    all_acc_dict = {}
    for item in list(unique_df['Корр_счет']):
        if item in all_acc_dict:
            all_acc_dict[item] += 1
        else:
            all_acc_dict[item] = 1
    logger.info(f'\nсчета и субсчета в нашем анализе и их количество: {all_acc_dict}')

    # счета с субсчетами
    acc_with_sub = [i for i in all_acc_dict if is_parent(i, all_acc_dict)]
    logger.info(f'\nсчета c субсчетами в нашем анализе: {acc_with_sub}')

    clean_acc = [i for i in all_acc_dict if i not in acc_with_sub]
    logger.info(f'\nочистка 1: {clean_acc}')
    clean_acc = [i for i in clean_acc if all_acc_dict[i] == 1]
    logger.info(f'\nочистка 2: {clean_acc}')
    del_acc = [i for i in all_acc_dict if i not in clean_acc]
    
    # список из 94 счетов, т.к основной счет 94.Н в серых 1с
    # к нему открыты субсчета 94, 94.01, 94.04
    # поэтому для серый 1с оставляем только 94.Н
    # в желтых 1с и так 94 счет без субсчетов
    acc_with_94 = [i for i in all_acc_dict if '94' in i]
    del_acc_with_94 = []
    if '94.Н' in acc_with_94:
        del_acc_with_94 = [i for i in acc_with_94 if i !='94.Н']
    del_acc = list(set(del_acc + del_acc_with_94))
    
    
    
    logger.info(f'n\финал для удаления: {del_acc}')
    
    df[sign_1c] = df[sign_1c].apply(lambda x: str(x))

    df = df[
        ~df[sign_1c].isin(exclude_values) &  # Исключение определенных значений (Сальдо, Оборот и т.д.)
        ~df[sign_1c].isin(del_acc) # Исключение счетов, по которым есть расшифровка субконто (60, 60.01 и т.д.)
        ].copy()
    
    df = df[df['Курсив'] == 0].copy()
    df[sign_1c] = df[sign_1c].astype(str)


    shiftable_level = 'Level_0'
    list_level_col = [i for i in df.columns.to_list() if i.startswith('Level')]
    for i in list_level_col[::-1]:
        if all(df[i].apply(is_accounting_code)):
            shiftable_level = i
            break
        
    df['Субсчет'] = df.apply(
        lambda row: row[shiftable_level] if (str(row[shiftable_level])!= '7') else f"0{row[shiftable_level]}",
        axis=1)  # 07 без субсчетов
    df['Субсчет'] = df.apply(
        lambda row: 'Без_субсчетов' if not is_accounting_code(row['Субсчет']) else row['Субсчет'], axis=1)
    
    if sign_1c == 'Кор.счет':
        df.rename(columns={sign_1c: 'Субконто_корр_счета', 'Счет': 'Аналитика'}, inplace=True)
    else:
        df.rename(columns={sign_1c: 'Субконто_корр_счета', 'Счет': 'Аналитика', 'Дебет': 'С кред. счетов',
                              'Кредит': 'В дебет счетов'}, inplace=True)

    logger.info(f'{file_excel}: переименовали некоторые столбцы по смыслу')

    # Указываем желаемый порядок для известных столбцов
    desired_order = ['Исх.файл', 'Субсчет', 'Аналитика', 'Корр_счет', 'Субконто_корр_счета', 'С кред. счетов', 'В дебет счетов']

    # Находим все столбцы, содержащие 'Level_'
    level_columns = [col for col in df.columns.to_list() if 'Level_' in col]

    # Объединяем известные столбцы с найденными столбцами 'Level_'
    new_order = desired_order + level_columns

    # Переупорядочиваем столбцы в DataFrame
    df = df[new_order]
    df.loc[:, 'Субконто_корр_счета'] = df['Субконто_корр_счета'].apply(
        lambda x: 'Не расшифровано' if is_accounting_code(x) else x)
    logger.info(f'{file_excel}: переупорядочили столбцы')

    df = df.dropna(subset=['С кред. счетов', 'В дебет счетов'], how='all')
    df = df[(df['С кред. счетов'] != 0) | (df['С кред. счетов'].notna())]
    df = df[(df['В дебет счетов'] != 0) | (df['В дебет счетов'].notna())]
    
    return df
