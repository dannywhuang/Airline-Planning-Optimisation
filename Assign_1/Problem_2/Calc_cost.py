import numpy as np
import pandas as pd
from datetime import datetime
import ast
from gurobipy import *
from objectLoader import save_obj



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
Duty_period =  pd.read_excel(File2, usecols = 'A:B', converters={'column_name': eval})
Hotel       =  pd.read_excel(File3, usecols = 'A:C')

Airports    =  Hotel.iloc[:, 0].to_numpy()
Room_fee    =  Hotel.iloc[:, 2].to_numpy()


Flights_duty     =  Duty_period.iloc[:, 1].apply(ast.literal_eval)

Flight_num  = Timetable.iloc[:, 0].to_numpy()
Origin      = Timetable.iloc[:, 1].to_numpy()
Destin      = Timetable.iloc[:, 2].to_numpy()
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
DurationNoBrief = np.zeros(len(Flights_duty))
DurationWithBrief = np.zeros(len(Flights_duty))
FlightCost = np.zeros(len(Flights_duty))
FixedCost = np.zeros(len(Flights_duty))
HotelCost = np.zeros(len(Flights_duty))

for i in range(len(Flights_duty)):
    Flight_cost = 0
    l  = Flights_duty[i]
    durationNoBrief = 0
    durationWithBrief = 0
    for j in l:
         index = list(Flight_num).index(j)
         h     = Flight_time[index]
         durationNoBrief += h
         durationWithBrief += h + 40/60
         cost_hour   =  (Cap_h + firstO_h +Steward_h)*(h+40/60) # add brief periods
         Flight_cost = Flight_cost  + cost_hour

    start_duty  = Origin[list(Flight_num).index(l[0])]
    end_duty    = Destin[list(Flight_num).index(l[-1])]

    if start_duty != end_duty:
        hotel_cost =  Room_fee[list(Airports).index(end_duty)] * 5  # 5 crew members
    else:
        hotel_cost = 0
    cost_fixed = Cap + firstO + Steward
    Cost[i] = Flight_cost + hotel_cost + cost_fixed
    HotelCost[i] = hotel_cost
    FlightCost[i] = Flight_cost
    FixedCost = cost_fixed
    DurationNoBrief[i] = durationNoBrief
    DurationWithBrief[i] = durationWithBrief

save_obj(Cost, 'cost')
save_obj(HotelCost, 'hotel_cost')
save_obj(FlightCost, 'flight_cost')
save_obj(FixedCost, 'fixed_cost')
save_obj(DurationNoBrief, 'duration_no_brief')
save_obj(DurationWithBrief, 'duration_with_brief')
np.savetxt('cost.csv',Cost,delimiter=',')

dpf = {}
for p in range(len(Flights_duty)):
    for f in range(len(Flight_num)):
        if Flight_num[f] in Flights_duty[p]:
            dpf[p, f] = 1
        else:
            dpf[p, f] = 0

save_obj(dpf, 'dpf')
print("Should be 1: ", dpf[33441, 133]) # verification, should give 1
print("Should be 0: ", dpf[33440, 133]) # verification, should give 0
print("Should be 1: ", dpf[136, 2]) # verification, should give 1
