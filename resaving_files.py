import sys
import win32com.client
from pathlib import Path

from logger import logger

def save_as_xlsx_not_alert(folder_path: str):

    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        logger.error(f"Неверный путь: {folder_path}. Скрипт завершен неудачно")
        sys.exit()

    excel_files_found = False
    sNewFolderPath = folder_path / "ConvertedFiles"

    for oFile in folder_path.iterdir():
        if oFile.suffix.lower() in ('.xls', '.xlsx'):
            excel_files_found = True
            break

    if excel_files_found:
        try:
            sNewFolderPath.mkdir(exist_ok=True)
        except OSError as e:
            logger.error(f"Ошибка создания новой папки: {e}. Скрипт завершен неудачно")
            sys.exit()
    else:
        logger.error("Файлы Excel не найдены. Скрипт завершен неудачно")
        sys.exit()

    for oFile in folder_path.iterdir():
        if oFile.suffix.lower() in ('.xls', '.xlsx'):
            file_path = oFile.resolve()

            if not file_path.is_file():
                logger.error(f"Файл не найден: {file_path}. Скрипт завершен неудачно")
                continue

            excel_app = None
            try:
                excel_app = win32com.client.Dispatch('Excel.Application')
                excel_app.Visible = False
                excel_app.DisplayAlerts = False

                wb = excel_app.Workbooks.Open(str(file_path))
                new_file_path = sNewFolderPath / (oFile.stem + '.xlsx')
                wb.SaveAs(str(new_file_path), FileFormat=51)
                logger.info(f'Файл {oFile.name} конвертирован {new_file_path.name}.')

                wb.Close(SaveChanges=False)
                excel_app.Quit()

            except Exception as e:
                logger.error(f"Ошибка обработки файла {oFile.name}: {e}")

            finally:
                if excel_app is not None:
                    excel_app.Quit()

    if sNewFolderPath is not None and not any(sNewFolderPath.iterdir()):
        logger.info("Преобразованные файлы не найдены. Скрипт завершен неудачно")
        sNewFolderPath.rmdir()
        sys.exit()