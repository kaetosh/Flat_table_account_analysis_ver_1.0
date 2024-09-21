import config

from logger import logger
from utility_functions import terminate_script, catch_errors


@catch_errors()
def table_header(df, file_excel):
    """
    Обновляем наименования столбцов на корректные
    """

    # Получаем индекс строки, содержащей target_value (значение)
    index_for_columns = None
    try:
        index_for_columns = df.index[df.apply(lambda row: config.target_value in row.values, axis=1)][0]
    except IndexError:
        terminate_script(f'{file_excel}: Не найдена строка со значением {config.target_value}')

    # Устанавливаем заголовки
    df.columns = df.iloc[index_for_columns]

    # Имена столбцов (в т.ч. np.nan) преобразуем в строки
    df.columns = df.columns.map(str)

    # Удаляем данные выше строки с именами столбцов таблицы (наименование отчета, период и т.д.)
    df.drop(df.index[0:(index_for_columns + 1)], inplace=True)

    # Переименуем первые два столбца
    df.columns.values[0] = 'Уровень'
    df.columns.values[1] = 'Курсив'
    logger.info(f'{file_excel}: успешно обновили шапку таблицы, удалили строки выше шапки')

    # Удаляем пустые строки и столбцы
    df.dropna(axis=0, how='all', inplace=True)
    if 'nan' in df.columns.to_list():
        df.drop(columns=['nan'], inplace=True)
    logger.info(f'{file_excel}: удалили пустые строки и столбцы')

    # Добавим столбец с названием файла
    df['Исх.файл'] = file_excel


