# # -*- coding: utf-8 -*-
# """
# Created on Wed Aug 28 16:36:46 2024
#
# @author: a.karabedyan
# """

import os
import win32com.client

from logger import logger
from settings import folder_path

def save_as_xlsx_not_alert():

    # Create a new folder for converted files
    sNewFolderPath = os.path.join(folder_path, "ConvertedFiles")
    if not os.path.exists(sNewFolderPath):
        os.makedirs(sNewFolderPath)

    # Iterate through all files in the selected folder
    for oFile in os.listdir(folder_path):
        # Check if the file is an Excel file
        if oFile.endswith(('.xls', '.xlsx')):
            # Open the Excel file
            excel = win32com.client.Dispatch('Excel.Application')
            excel.Visible = False  # Hide Excel application
            excel.DisplayAlerts = False  # Disable alerts
            wb = excel.Workbooks.Open(os.path.join(folder_path, oFile))

            # Save the file as xlsx
            wb.SaveAs(os.path.join(sNewFolderPath, os.path.splitext(oFile)[0] + '.xlsx'), FileFormat=51)

            # Close the workbook without saving changes
            wb.Close(SaveChanges=False)
            logger.info(f'Исходный файл {oFile} пересохранен.')
            print(f'Исходный файл {oFile} пересохранен.')

    # Quit Excel application
    excel.Quit()

    # Display a message box
    logger.info('Исходные файлы Excel пересохранены.')
    print('Все исходные файлы Excel пересохранены.')

