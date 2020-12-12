import numpy as np
import pandas as pd
from datetime import datetime
import ast
# ________________________________
# fixed cost per day
Cap      = 98
firstO  = 35
Steward  = 15*3    # 3 persons

# fixed cost per h
Cap_h      = 120
firstO_h   = 55
Steward_h  = 18*3  # 3 persons
# ________________________________

File1       = '1_Timetable_Group_34.xlsx'
File2       = '2_Duty_Periods_Group_34.xlsx'
File3       = '3_Hotel_Costs_Group_34.xlsx'

Timetable   =  pd.read_excel(File1, usecols = 'A:E')
Duty_period =  pd.read_excel(File2, usecols = 'A:B')
Hotel       =  pd.read_excel(File3, usecols = 'A:C')

Airports    =  Hotel.iloc[:, 0].to_numpy()
Room_fee    =  Hotel.iloc[:, 2].to_numpy()

Flights_duty     =  Duty_period.iloc[:, 1].to_numpy()

Flight_num  = Timetable.iloc[:, 0].to_numpy()
Origin      = Timetable.iloc[:, 1].to_numpy()
T_start     = Timetable.iloc[:, 3].to_numpy()
T_end       = Timetable.iloc[:, 4].to_numpy()


FMT = '%H:%M:%S'
Flight_time = np.zeros(len(T_start))
for i in range(len(T_start)):
     t2 =   T_end[i]
     t1 =   T_start[i]
     td = datetime.strptime(t2, FMT) - datetime.strptime(t1, FMT)
     hours  = td.seconds/3600
     Flight_time[i] = hours

Cost = np.ones(len(Flights_duty))

for i in range(len(Flights_duty)):
    Flight_cost = 0
    l  = ast.literal_eval(Flights_duty[i])
    for j in l:
         index = list(Flight_num).index(j)
         h     = Flight_time[index]
         cost_hour   =  (Cap_h + firstO_h +Steward_h)*(h+40/60) # add brief periods
         Flight_cost = Flight_cost  + cost_hour
    if l[0] != l[-1]:
        Base = Origin[list(Flight_num).index(l[0])]
        hotel_cost =  Room_fee[list(Airports).index(Base)] * 5  # 5 crew members
    else:
        hotel_cost = 0
    cost_fixed = Cap + firstO + Steward
    Cost[i] = Flight_cost + hotel_cost + cost_fixed

