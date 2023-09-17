# -*- coding: utf-8 -*-
'Tarea Albert'

import pandas as pd

data = {
    'ID_Estudiante': [101, 102, 103, 104, 105],
    'Nombre': ['Marta', 'Jorge', 'Pilar', 'Charly', 'Mariana'],
    'Matemática': [85, 90, 78, 92, 88],
    'Historia': [92, 90, 84, 76, 80],
    'Biología': [89, 92, 79, 85, 90],
    'Arte': [72, 76, 85, 80, 88],
    'Promedio': [84.5, 87, 81.5, 83.25, 86.5]
}

df = pd.DataFrame(data)


'Ejercicios de Navegacion'
# Mostrar las primeras 3 filas

tres_primeras_filas = df.head(3)
print(tres_primeras_filas)

# Mostrar las 2 últimas filas
dos_ultimas_filas = df.tail(2)
print(dos_ultimas_filas)

#Mostras los primeros 3 estudiantes, pero solo ID y Nombre
id_y_nombre = df.loc[:2,['ID_Estudiante','Nombre']]
id_y_nombre2 = df.head(3)[['ID_Estudiante', 'Nombre']]

print(id_y_nombre)

#Mostrar cuanto saco en Matematicas estudiante con ID 104. El valor tiene que
#ser un entero, no una Serie,ni un array

ID_104_matematicas = int(df[df['ID_Estudiante'] == 104]['Matemática'])

print(df[df['ID_Estudiante'] == 104]['Nombre'].values[0] + " obtuvo " 
      + str(ID_104_matematicas) + " en Matemáticas")


#Cambiar Calificacion de historia a 77
df_cambio_calificacion = df.copy()
df_cambio_calificacion.loc[df_cambio_calificacion['ID_Estudiante'] == 102, 'Historia'] = 77

#Recalcular promedios
df_cambio_calificacion['Promedio'] = df_cambio_calificacion.iloc[:, 2:6].mean(axis=1)

#Mostrar estudiantes que hayan sacando mas de 80 en arte
df_arte = df[df['Arte'] > 80]

#Estudiante que hayan sacado mas de 80 en Matematicas y menos de 85 en historia
df_mate_historia = df[(df['Matemática']>80) & 
                      (df['Historia']<85)]

df_mate_historia_nombres = df[(df['Matemática']>80) & 
                      (df['Historia']<85)]['Nombre']


#Estudiante con mejor promedio
# Mostrar al estudiante con el mejor promedio en un DataFrame
df_mejor_promedio = df[df['Promedio'] == df['Promedio'].max()]
df_mejor_promedio_nombre = df_mejor_promedio['Nombre'].values[0]
df_mejor_promedio_numero = df_mejor_promedio['Promedio'].values[0]
print("El estudiante com mejor promedio fue: " + 
      str(df_mejor_promedio_nombre) + 
      '. \nObtuvo: ' + str(df_mejor_promedio_numero)
      )
      
      
      
      
      