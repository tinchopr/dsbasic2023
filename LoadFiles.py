# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 19:53:50 2023

@author: tinch

"""

#import any excel file from excel to a pandas DF

from datetime import datetime
import openpyxl
import os
import pandas as pd


import tkinter as tk
from tkinter import filedialog


def import_excel_file(path):
    
    # Extract filename from path
    filename = os.path.basename(path)
    
    # Replace with the path to your Excel workbook
    workbook_path = path
    
    # Load the workbook
    workbook = openpyxl.load_workbook(workbook_path, data_only=True)
    
   
    #Create a dictionary to store the dataframes
    workbook_sheets = {} #store the workbook as it is
    
    # Function to check if a string represents a valid date
    def is_valid_date(date_string):
        date_formats = ["%m/%d/%Y", "%m/%d/%y"]  # Add or change formats as needed
        for fmt in date_formats:
            try:
                datetime.strptime(date_string, fmt)
                return True
            except ValueError:
                continue
        return False
    
    # #Loop through each sheet and create a dataframe with the sheet data
    for sheet in workbook:
        df = pd.DataFrame(sheet.values)
        df = df.fillna("").replace(0,"")
        df = df[df.astype(bool).any(axis=1)]  # Drop rows where all columns are empty
        df = df.loc[:, df.astype(bool).any(axis=0)] 
        workbook_sheets[sheet.title] = df
    
    return {filename: workbook_sheets} 
  
def import_csv_file(path):
    # Load and convert the csv file to a dataframa
    # Strip out the filename from the path
    df_csv = pd.read_csv(path)
    csv_filename = os.path.basename(path)
    
    # Make a dictionary with the same structure as the one returned by the
    # import_excel_file function. The "sheet title" is the filename without the extension.
    return {csv_filename: {os.path.splitext(csv_filename)[0]: df_csv}}
    
  
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to select multiple files.
    workbook_paths = filedialog.askopenfilenames(filetypes=[("Excel and CSV Files", "*.xlsx *.xls *.csv")])
    
    workbook_sheets = {}

    for path in workbook_paths:
        ext = os.path.splitext(path)[1]
        if ext in [".xlsx", ".xls"]:
            workbook_sheets.update(import_excel_file(path))
            print(f"Processed Excel file: {os.path.basename(path)}")
        elif ext == ".csv":
            workbook_sheets.update(import_csv_file(path))
            print(f"Processed CSV file: {os.path.basename(path)}")
        