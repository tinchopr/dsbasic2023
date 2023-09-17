# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 20:43:39 2023

@author: tinch
"""

from LoadFiles import import_excel_file

pepe_sheets = {}


path = r"C:\Users\tinch\Downloads\Tucson.xlsx"
pepe_sheets.update(import_excel_file(path))