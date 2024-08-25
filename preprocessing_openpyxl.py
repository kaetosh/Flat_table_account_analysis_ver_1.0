import sys

import openpyxl
from logger import logger


def preprocessing_file_excel(path_file_excel):
    file_excel = path_file_excel.split('/')[-1]
    file_excel_treatment = f'preprocessing_files/preprocessing_{file_excel}'
    try:
        workbook = openpyxl.load_workbook(path_file_excel)
    except Exception as e:
        logger.error(f'''\n{file_excel}: Косячный файл-выгрузка из 1с, пересохраните этот файл и снова запустите скрипт.
                      Или открыт обрабатываемый файл. Закройте этот файл и снова запустите скрипт.
                      Ошибка: {e}''')
        sys.exit()

    sheet = workbook.active

    # Снимаем объединение ячеек
    merged_cells_ranges = list(sheet.merged_cells.ranges)
    for merged_cell_range in merged_cells_ranges:
        sheet.unmerge_cells(str(merged_cell_range))

    # Столбец с уровнями группировок
    sheet.insert_cols(idx=1)
    for row_index in range(1, sheet.max_row + 1):
        cell = sheet.cell(row=row_index, column=1)
        cell.value = sheet.row_dimensions[row_index].outline_level
    sheet['A1'] = "Уровень"

    # Столбец с признаком курсив
    sheet.insert_cols(idx=2)
    sheet['B1'] = "Курсив"

    for row in sheet.iter_rows(values_only=True):
        if "Счет" in row:
            try:
                kor_schet_col_index = row.index("Кор.счет") + 1  # We add 1 because indexing starts from 0
            except ValueError:
                try:
                    kor_schet_col_index = row.index("Кор. Счет") + 1
                except ValueError:
                    logger.error(f'''\n{file_excel}: Не обнаружен столбец 'Кор.счет' или 'Кор. Счет'.
                    Убедитесь, что обрабатываемый файл является Анализом счета.
                    Иначе сообщите разработчику,
                    если имя столбца с корреспондирующими счетами отличается от предложенного выше''')
                    workbook.close()
                    sys.exit()
            break
    else:
        logger.error(f'''\n{file_excel}: Не обнаружена строка в файле, содержащая поле 'Счет'.
                            Убедитесь, что обрабатываемый файл является Анализом счета.
                            Также возможно в анализе счета не указана группировка. 
                            Иначе сообщите разработчику,
                            если имя столбца отличается от предложенного выше''')
        workbook.close()
        sys.exit()

    # Мы заполняем новый столбец значениями, основанными на форматировании ячеек курсивом
    for row_index in range(2, sheet.max_row + 1):  # We start with 2 to skip the title
        kor_schet_cell = sheet.cell(row=row_index, column=kor_schet_col_index)
        new_cell = sheet.cell(row=row_index, column=2)
        new_cell.value = 1 if kor_schet_cell.font and kor_schet_cell.font.italic else 0

    workbook.save(file_excel_treatment)
    workbook.close()
    logger.info(f'\n{file_excel}: сняли объединение ячеек, проставли уровни группировок и признак курсив в ячейках')
    return file_excel_treatment
