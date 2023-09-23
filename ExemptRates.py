import pandas as pd
import PyPDF4
import io
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import xlwings as xw

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


# This function remains the same
def extract_text_from_pdf(url):
    response = requests.get(url)
    pdf_file_object = io.BytesIO(response.content)
    pdf_reader = PyPDF4.PdfFileReader(pdf_file_object)
    count = pdf_reader.numPages
    text = ""
    for i in range(count):
        page = pdf_reader.getPage(i)
        text += page.extractText()
    return text

# Get the active workbook and sheet
wb = xw.books.active
ws = wb.sheets['ExemptRates']

# Create a DataFrame from the active sheet's data
exempt_rate_table = ws.range('A1').expand().options(pd.DataFrame, index=False, header=True).value

# Create a new column for the address of month
exempt_rate_table['address'] = ['A' + str(i) for i in range(2, len(exempt_rate_table) + 2)]

# Set 'month' as index
exempt_rate_table.set_index('Month', inplace=True)

# make a request to the IRS main page
url = 'https://www.irs.gov/applicable-federal-rates'

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# I moved the regex pattern outside of the loop to avoid unnecessary recompilation
# REGEX_TEXT_TO_FIND = re.compile(r"Long\s*-\s*term\s*\n*\s*\n*adjusted\s*AFR\s*([\s\S]{6})")  
REGEX_TEXT_TO_FIND = re.compile(r"and\s*the\s*prior\s*two\s*months.\)\s*([\s\S]{10})")


# create list to store the extracted data
data = []
pdf_counter = 0


# Here we go through all 'a' elements in the page
for link in soup.find_all('a'):

    # Check if href exists and meets your conditions
    href = link.get('href')
    if href and href.endswith('.pdf') and 'rr' in href:  
        pdf_path = "https://www.irs.gov" + href
        
        if pdf_path not in exempt_rate_table['Link'].values:
            
            # Extract full text from the PDF link
            full_text = extract_text_from_pdf(pdf_path)
    
            # Initialize dictionary to store data for each link
            link_data = {'link': pdf_path}
    
            # Extract rate using regex
            match = REGEX_TEXT_TO_FIND.search(full_text)
            link_data['rate'] = match.group(1) if match else None
    
            # Remove line breaks from the rate if it exists 
            if link_data.get('rate'):
                link_data['rate'] = link_data['rate'].replace('\n', '')
            
            # Remove characters that are not numbers or periods
            link_data['rate'] = re.sub(r'[^0-9.]', '', link_data['rate']) if link_data.get('rate') else None
    
            # Extract the previous 30 characters before "(the current month)"
            start_position = full_text.find("(the current month)")
            if start_position != -1:
                start = max(start_position - 30, 0)  # Using max to handle negative start index
                previous_30_characters = full_text[start:start_position]
                link_data['month'] = previous_30_characters
            else:
                link_data['month'] = None
    
            # Append link_data to data
            data.append(link_data)
        # else:
        #     sys.exit()

# #Exit the code if not updated is needed
# if pdf_counter == 0:
#     sys.exit()

#Convert to number
# Define a function to clean the values and convert them to percentages
def convert_to_number(x):
    x = x.replace('\n','')  # This removes line breaks
    x = x.replace('%','')  # This removes line breaks
    x = re.sub(r'(\d) (\d)', r'\1\2', x)  # This removes any space between two numbers
    x = float(x)
    return x

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)
df['rate'] = df['rate'].apply(convert_to_number)

# Define a function to clean the values and convert them to percentages
def clean_text(x):
    x = x.replace('\n','')  # This removes line breaks
    x = re.sub(r'(\d) (\d)', r'\1\2', x)  # This removes any space between two numbers
    return x

#Clean Month DF
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

#Convert Month to date format
df['month'] = df['month'].apply(convert_to_date_format)
df['month'] = pd.to_datetime(df['month'], format='%m/%Y')

# Set 'month' as index
df.set_index('month', inplace=True)

# Sorting DataFrame by 'month' index
df.sort_index(inplace=True)

# Rearrange the columns
df = df[['rate','link']]

#Transform rates to %
df['rate'] = df['rate']/100

# #Merge Exempt Rata DF and 
final_df = exempt_rate_table.merge(df, left_index=True, right_index=True)
final_df = final_df.rename(columns={'link': 'IRS Link'})
final_df = final_df[final_df['Link'].isnull()]
final_df = final_df.drop(['Link',final_df.columns[0]],axis=1)

for index, row in final_df.iterrows():
    # print(row['address'], row['rate'], row['IRS Link'])
    ws.range(row['address']).offset(0,1).value = row['rate']
    ws.range(row['address']).offset(0,2).value = row['IRS Link']