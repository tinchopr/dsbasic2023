# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 19:32:15 2023

@author: tinch
"""

#Fiestas Paisanas
import pandas as pd
import requests
from io import StringIO


#Reemplazar \ por /
def replace_backslash_with_forwardslash(input_string):
    output_string = input_string.replace("\\", "/")
    return output_string

url = "https://datos.cultura.gob.ar/dataset/0560ef96-55ca-4026-b70a-d638e1541c05/resource/d948730c-e029-49c2-b63d-86fac65ac30a/download/10_fiestaspopulares_festivales-datos_abiertos-2.csv"
# path = replace_backslash_with_forwardslash(path)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

response = requests.get(url, headers=headers)
data = response.content.decode('utf-8')

df = pd.read_csv(StringIO(data))
df2 = df.copy()
df_chaco = df2[df2['Provincia '] == "Chaco"]
df_chaco = df_chaco[df_chaco['último año de realizacion']!='s/d']

df3 = df

df3.iloc[0,2] = "PEPITO"
