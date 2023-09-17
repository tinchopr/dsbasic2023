import pandas as pd
import PyPDF4
import io
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
# import xlwings as xw

'''
La idea de este programa es descargar una tasa específica de una pógina del 
IRs que sino se tiene que hacer manual.
Estas micro tares, cuando sumadas llevan mucho tiempo y distraen

#Para auditar elque quiera, la tasa que baja corresponde a:
    

Long-term tax-exempt rate for ownership changes during the
current month (the highest of the adjusted federal long-term
rates for the current month and the prior two months.)  ====> 1.57%

En el caso por ejemplo de Septiembre 2021: https://www.irs.gov/pub/irs-drop/rr-21-16.pdf

o

En el caso por ejemplo de Octubre 2021: https://www.irs.gov/pub/irs-drop/rr-21-16.pdf
Long-term tax-exempt rate for ownership changes during the
current month (the highest of the adjusted federal long-term
rates for the current month and the prior two months.) 1.44%

'''
### COMIENZO DEL PROGRAMA    

# Esta función se encarga de extraer el texto de un archivo PDF a partir de una URL específica. Primero,
# realiza una solicitud a la URL proporcionada y obtiene el contenido de respuesta, que es el archivo PDF en sí.
# Luego, crea un objeto de archivo PDF con el contenido de respuesta y utiliza el lector de PDF PyPDF2 para leerlo.
# Después obtiene el número total de páginas en el archivo PDF y inicializa una variable de texto vacía.
# Recorre cada página del archivo PDF y extrae el texto de dicha página, el cual se va acumulando en la variable de texto.
# Finalmente, devuelve el texto acumulado que es el contenido completo del archivo PDF.


def extract_text_from_pdf(url):
    response = requests.get(url)
    pdf_file_object = io.BytesIO(response.content)
    # pdf_reader = PyPDF2.PdfFileReader(pdf_file_object)
    pdf_reader = PyPDF4.PdfFileReader(pdf_file_object)  
    count = pdf_reader.numPages
    text = ""
    for i in range(count):
        page = pdf_reader.getPage(i)
        text += page.extractText()
    return text

'''
Parte comentada dado que específicio para un excel del trabajo
'''
##############################

# # Obtén el libro de trabajo activo y la hoja
# wb = xw.books.active
# ws = wb.sheets['ExemptRates']

# # Crea un DataFrame a partir de los datos de la hoja activa
# exempt_rate_table = ws.range('A1').expand().options(pd.DataFrame, index=False, header=True).value

# # Crea una nueva columna para la dirección del mes
# exempt_rate_table['address'] = ['A' + str(i) for i in range(2, len(exempt_rate_table) + 2)]

# # Establece 'month' como índice
# exempt_rate_table.set_index('Month', inplace=True)

##############################

'''
Sigue el programa
'''

# Realiza una solicitud a la página principal del IRS
url = 'https://www.irs.gov/applicable-federal-rates'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Esta línea de código crea una "plantilla" que nos ayuda a encontrar partes específicas del texto. Se hace una sola vez para ahorrar tiempo.
REGEX_TEXT_TO_FIND = re.compile(r"and\s*the\s*prior\s*two\s*months.\)\s*([\s\S]{10})")

# Crea una lista para almacenar los datos extraídos
data = []
pdf_counter = 0


# Aquí recorremos todos los elementos 'a' en la página
for link in soup.find_all('a'):

    # Verifica si href existe y cumple tus condiciones
    href = link.get('href')
    if href and href.endswith('.pdf') and 'rr' in href:  
        pdf_path = "https://www.irs.gov" + href
        
        # if pdf_path not in exempt_rate_table['Link'].values:
            
        # Extrae el texto completo del enlace PDF
        full_text = extract_text_from_pdf(pdf_path)

        # Inicializa el diccionario para almacenar los datos de cada enlace
        link_data = {'link': pdf_path}

        # Extrae la tasa usando regex
        match = REGEX_TEXT_TO_FIND.search(full_text)
        link_data['rate'] = match.group(1) if match else None

        # Elimina los saltos de línea de la tasa si existe
        if link_data.get('rate'):
            link_data['rate'] = link_data['rate'].replace('\n', '')
        
        # Elimina los caracteres que no son números o puntos
        link_data['rate'] = re.sub(r'[^0-9.]', '', link_data['rate']) if link_data.get('rate') else None

        # Extrae los 30 caracteres anteriores a "(el mes actual)"
        start_position = full_text.find("(the current month)")
        if start_position != -1:
            start = max(start_position - 30, 0)  # Utilizando max para manejar un índice de inicio negativo
            previous_30_characters = full_text[start:start_position]
            link_data['month'] = previous_30_characters
        else:
            link_data['month'] = None

        # Agrega link_data a los datos
        data.append(link_data)

#Convertir a número
# Define una función para limpiar los valores y convertirlos en porcentajes
def convert_to_number(x):
    x = x.replace('\n','')  # Esto elimina los saltos de línea
    x = x.replace('%','')  # Esto elimina los saltos de línea
    x = re.sub(r'(\d) (\d)', r'\1\2', x)  # Esto elimina cualquier espacio entre dos números
    x = float(x)
    return x

# Convierte la lista de diccionarios en un DataFrame
df = pd.DataFrame(data)
df['rate'] = df['rate'].apply(convert_to_number)

# Define una función para limpiar los valores y convertirlos en porcentajes
def clean_text(x):
    x = x.replace('\n','')  # Esto elimina los saltos de línea
    x = re.sub(r'(\d) (\d)', r'\1\2', x)  # Esto elimina cualquier espacio entre dos números
    return x

#Limpia Mes del DF
df['month'] = df['month'].apply(clean_text)

def extract_date(x):
    match = re.findall(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})", x)
    return match[0] if match else ('', '')

df['month'] = df['month'].apply(extract_date)

def convert_to_date_format(x):
    try:
        return datetime.strptime(' '.join(x), "%B %Y").strftime('%m/%Y')
    except ValueError:
        return ''

#Convierte Mes a formato de fecha
df['month'] = df['month'].apply(convert_to_date_format)
df['month'] = pd.to_datetime(df['month'], format='%m/%Y')

# Establece 'month' como índice
df.set_index('month', inplace=True)

#Ordena DataFrame por índice 'month'
df.sort_index(inplace=True)

# Reorganiza las columnas
df = df[['rate','link']]

#Transforma las tasas a %
df['rate'] = df['rate']/100

# Imprime resultados en la consola
print(df)

'''
Parte comentada dado que específicio para un excel del trabajo
'''
##############################
# # Fusiona el DataFrame de Tasa Exenta y 
# final_df = exempt_rate_table.merge(df, left_index=True, right_index=True)
# final_df = final_df.rename(columns={'link': 'IRS Link'})
# final_df = final_df[final_df['Link'].isnull()]
# final_df = final_df.drop(['Link',final_df.columns[0]],axis=1)

# for index, row in final_df.iterrows():
#     ws.range(row['address']).offset(0,1).value = row['rate']
#     ws.range(row['address']).offset(0,2).value = row['IRS Link']

##############################