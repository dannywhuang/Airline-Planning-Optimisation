import numpy as np
import pandas as pd
from datetime import datetime
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
Hotel       =  pd.read_excel(File3, usecols = 'A:c')

Flights_duty     =  Duty_period.iloc[:, 1].to_numpy()

Flight_num  = Timetable.iloc[:, 0].to_numpy()

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

Flights_duty = np.array([Flights_duty[i][1:-1] for i in range(len(Flights_duty))])
Flights_duty = np.array([i.replace("'", '') for i in Flights_duty ])




Cost = np.ones(len(Flights_duty))

for i in range(len(Flights_duty)):
    Flight_cost = 0
    l = Flights_duty[i].split(", ")
    for j in l:
         index = list(Flight_num).index(j)
         h     = Flight_time[index]
         cost_fixed  =  Cap + firstO + Steward
         cost_hour   =  (Cap_h + firstO_h +Steward_h)*h
         Flight_cost = Flight_cost + cost_fixed + cost_hour
    if l[0] != l[-1]:
        hotel_cost = 1  # add costs from file for
    else:
        hotel_cost = 0

    Cost[i] = Flight_cost + hotel_cost

