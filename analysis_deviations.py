from logger import logger

from utility_functions import is_accounting_code


def revolutions_before_processing(df, file_excel, sign_1c, debet_name, credit_name):
    df_for_check = df[[sign_1c, debet_name, credit_name]].copy()
    df_for_check['Кор.счет_ЧЕК'] = df_for_check[sign_1c].apply(lambda x: x if is_accounting_code(x) else None).copy()
    df_for_check = df_for_check.dropna(subset=['Кор.счет_ЧЕК'])
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].fillna('')
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].astype(str)
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].apply(lambda x: f'0{x}' if len(x) == 1 else x)
    
    if '94.Н' in df_for_check['Кор.счет_ЧЕК'].values:
        df_for_check = df_for_check[
        (df_for_check['Кор.счет_ЧЕК'] == '94.Н') | 
        (df_for_check['Кор.счет_ЧЕК'].str.match(r'^\d{2}$') & 
         ~df_for_check['Кор.счет_ЧЕК'].isin([str(x) for x in range(94, 95)]))
    ].copy()
    
    else:
        df_for_check = df_for_check[df_for_check['Кор.счет_ЧЕК'].str.match(r'^\d{2}$')].copy()
    
    df_for_check['Кор.счет_ЧЕК'] = df_for_check['Кор.счет_ЧЕК'].replace('94.Н', '94')
    df_for_check = df_for_check.groupby('Кор.счет_ЧЕК')[[debet_name, credit_name]].sum().copy()
    df_for_check = df_for_check.reset_index()
    if sign_1c != 'Кор.счет':
        df_for_check.rename(columns={'Дебет': 'С кред. счетов', 'Кредит': 'В дебет счетов'}, inplace=True)
    logger.info(f'{file_excel}: сформировали таблицу с оборотами в разрезе счетов до обработки')
    return df_for_check

def revolutions_after_processing(df, df_for_check, file_excel):
    df_for_check_2 = df[['Корр_счет', 'С кред. счетов', 'В дебет счетов']].copy()

    df_for_check_2['Корр_счет'] = df_for_check_2['Корр_счет'].astype(str).copy()
    df_for_check_2['Кор.счет_ЧЕК'] = df_for_check_2['Корр_счет'].apply(lambda x: x[:2] if len(x) >= 2 else x).copy()
    df_for_check_2 = df_for_check_2.groupby('Кор.счет_ЧЕК')[['С кред. счетов', 'В дебет счетов']].sum().copy()
    df_for_check_2 = df_for_check_2.reset_index()

    # Объединение DataFrame с использованием внешнего соединения
    merged_df = df_for_check.merge(df_for_check_2, on='Кор.счет_ЧЕК', how='outer',
                                   suffixes=('_df_for_check', '_df_for_check_2'))

    # Заполнение отсутствующих значений нулями
    merged_df = merged_df.infer_objects().fillna(0)

    # Вычисление разницы
    merged_df['Разница_С_кред'] = merged_df['С кред. счетов_df_for_check'] - merged_df['С кред. счетов_df_for_check_2']
    merged_df['Разница_В_дебет'] = merged_df['В дебет счетов_df_for_check'] - merged_df['В дебет счетов_df_for_check_2']

    merged_df['Разница_С_кред'] = merged_df['Разница_С_кред'].apply(lambda x: round(x))
    merged_df['Разница_В_дебет'] = merged_df['Разница_В_дебет'].apply(lambda x: round(x))

    merged_df['Исх.файл'] = file_excel
    logger.info(f'{file_excel}: сформировали дополнительную таблицу с отклонениями до и после обработки')
    return merged_df
