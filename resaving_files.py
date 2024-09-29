import win32com.client
from pathlib import Path
import config
from utility_functions import terminate_script, logger_with_spinner

# выгрузки из 1С УПП не загружаются в openpyxl без пересохранения Excel-ем
# пересохранение файлов
def save_as_xlsx_not_alert():
    folder_path = Path(config.folder_path)
    if not folder_path.is_dir():
        terminate_script(f"Неверный путь: {folder_path}. Скрипт завершен неудачно.")

    sNewFolderPath = folder_path / "ConvertedFiles"
    sNewFolderPath.mkdir(exist_ok=True)

    excel_files_found = False
    for oFile in folder_path.iterdir():
        if oFile.suffix.lower() in ('.xls', '.xlsx'):
            excel_files_found = True
            break

    if not excel_files_found:
        sNewFolderPath.rmdir()  # Delete the empty ConvertedFiles folder
        terminate_script("Файлы Excel не найдены. Скрипт завершен неудачно.")

    excel_app = win32com.client.Dispatch('Excel.Application')
    excel_app.Visible = False
    excel_app.DisplayAlerts = False

    try:
        for oFile in folder_path.iterdir():
            if oFile.suffix.lower() in ('.xls', '.xlsx'):
                file_path = oFile.resolve()
                if not file_path.is_file():
                    logger_with_spinner(f"Файл не найден: {file_path}.", warning_log=True)
                    continue

                wb = excel_app.Workbooks.Open(str(file_path))
                new_file_path = sNewFolderPath / (oFile.stem + '.xlsx')
                wb.SaveAs(str(new_file_path), FileFormat=51)
                logger_with_spinner(f'File {oFile.name} converted to {new_file_path.name}.')
                wb.Close(SaveChanges=False)
    except Exception as e:
        sNewFolderPath.rmdir()  # Delete the ConvertedFiles folder if an error occurs
        terminate_script(f"Ошибка обработки файла: {e}")
    finally:
        excel_app.Quit()

    if not any(sNewFolderPath.iterdir()):
        sNewFolderPath.rmdir()  # Delete the empty ConvertedFiles folder
        terminate_script("Обработанные файлы не найдены. Скрипт завершен неудачно.")