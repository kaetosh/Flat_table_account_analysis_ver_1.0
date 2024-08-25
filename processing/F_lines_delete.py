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

def lines_delete(df, sign_1c):
    df_delete = df[~df[sign_1c].isin(exclude_values)]
    df_delete = df_delete.dropna(subset=[sign_1c]).copy()
    df_delete = df_delete[df_delete['Курсив'] == 0][[sign_1c, 'Корр_счет']]

    required_prefixes = ['58', '60', '62', '63', '66', '67', '75', '76']
    logger.info(f'\nВсе счета, где есть субконто Контрагент required_prefixes: {required_prefixes}')

    unique_df = df_delete.drop_duplicates(subset=[sign_1c, 'Корр_счет'])

    count_dict0 = {}
    for item in list(unique_df['Корр_счет']):
        if item in count_dict0:
            count_dict0[item] += 1
        else:
            count_dict0[item] = 1
    logger.info(f'\nсчета и субсчета в нашем анализе и их количество: {count_dict0}')
    values_filtr = accounting_code_without_subaccount(
        df[df['Корр_счет'].apply(is_accounting_code)]['Корр_счет'].unique())
    logger.info(f'\nсчета в нашем анализе без субсчетов values_filtr: {values_filtr}')

    list_key_count_dict0 = [i for i in count_dict0]
    logger.info(f'\nсписок ключей словаря со счетами и субсчетами list_key_count_dict0: {list_key_count_dict0}')

    # Преобразование списков в множества
    set1 = set(list_key_count_dict0)
    set2 = set(values_filtr)

    # Найти пересечение множеств
    intersection = set1.intersection(set2)

    # Вывод результата
    logger.info(f'\nсчета в нашем анализе без субсчетов intersection: {intersection}')

    # Преобразование списков в множества
    set11 = set(required_prefixes)
    set22 = set(intersection)

    # Найти разность множеств
    difference = set11.difference(set22)

    # Преобразование разности множеств обратно в список
    difference_list = list(difference)

    # Вывод результата
    logger.info(f'\nсписок ключей для удаления из list_key_count_dict0 difference_list: {difference_list}')

    for i in difference_list:
        try:
            count_dict0.pop(i)
        except KeyError:
            continue
    logger.info(f'\nполучили обновленный словарь со счетами в нашем анализе, где есть субконто Контрагент count_dict0: {count_dict0}')

    keys_with_positive_values = []
    for key, value in count_dict0.items():
        if value > 1:
            keys_with_positive_values.append(key)

    # Вывод результата
    logger.info(f'\nполучили счета в нашем анализе, где включена расшифровка Контрагент keys_with_positive_values: {keys_with_positive_values}')

    parent_accounts = []
    for account in keys_with_positive_values:
        for parent in get_parent_accounts(account):
            if account != parent and parent not in parent_accounts:
                parent_accounts.append(parent)
        parent_accounts.append(account)  # добавляем исходный счет в список родительских счетов
    parent_accounts = list(set(parent_accounts))  # удаляем дубликаты из списка

    logger.info(f'\nполучили финальные счета и субсчета, где включена расшифровка Контрагент parent_accounts: {parent_accounts}')

    values_filtr_clear = [value for value in values_filtr if value not in parent_accounts]
