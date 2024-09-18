"""
Обновляем наименования столбцов на корректные
"""

from settings import target_value
from logger import logger


def table_header(df, file_excel):
    # получаем индекс строки, содержащей target_value (значение)
    index_for_columns = df.index[df.apply(lambda row: target_value in row.values, axis=1)][0]

    # устанавливаем заголовки
    df.columns = df.iloc[index_for_columns]

    # Имена столбцов (в т.ч. np.nan) преобразуем в строки
    df.columns = df.columns.map(str)

    # удаляем данные выше строки с именами столбцов таблицы (наименование отчета, период и т.д.)
    df.drop(df.index[0:(index_for_columns + 1)], inplace=True)
    
    

    # переименуем первые два столбца
    df.columns.values[0] = 'Уровень'
    df.columns.values[1] = 'Курсив'
    logger.info(f'{file_excel}: успешно обновили шапку таблицы, удалили строки выше шапки')

    # удаляем пустые строки и столбцы
    df.dropna(axis=0, how='all', inplace=True)
    if 'nan' in df.columns.to_list():
        df.drop(columns=['nan'], inplace=True)
    logger.info(f'{file_excel}: удалили пустые строки и столбцы')
    


    # Добавим столбец с названием файла
    df['Исх.файл'] = file_excel
