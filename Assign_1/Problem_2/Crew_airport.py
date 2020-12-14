import numpy as np
import pandas as pd
import ast
from objectLoader import load_obj

File1       = '1_Timetable_Group_34.xlsx'
File2       = '2_Duty_Periods_Group_34.xlsx'
File3       = '3_Hotel_Costs_Group_34.xlsx'

Timetable   =  pd.read_excel(File1, usecols = 'A:E')
Duty_period =  pd.read_excel(File2, usecols = 'A:B', converters={'column_name': eval})
Hotel       =  pd.read_excel(File3, usecols = 'A:C')

Airports    =  Hotel.iloc[:, 0].to_numpy()
Room_fee    =  Hotel.iloc[:, 2].to_numpy()


Flights_duty     =  Duty_period.iloc[:, 1].apply(ast.literal_eval)

Flight_num  = Timetable.iloc[:, 0].to_numpy()
Origin      = Timetable.iloc[:, 1].to_numpy()
Destin      = Timetable.iloc[:, 2].to_numpy()

pairings = load_obj('pairing')

crew = pd.DataFrame(np.zeros(len(Airports)), index=Airports)

for i in pairings:
    l = Flights_duty[i]
    base = Origin[list(Flight_num).index(l[0])]
    crew.loc[base]+=1
