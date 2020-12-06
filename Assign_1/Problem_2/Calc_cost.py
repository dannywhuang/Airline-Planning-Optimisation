import numpy as np
import pandas as pd
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
Hotel_cost  = '3_Hotel_Costs_Group_34.xlsx'

Timetable   =  pd.read_excel(File1, usecols = 'A:E')
Duty_period =  pd.read_excel(File2, usecols = 'A:B')

Flights_duty     =  Duty_period.iloc[:, 1]

Flight_num  = Timetable.iloc[:, 0].to_numpy()

T_start     = Timetable.iloc[:, 3].to_numpy()
T_end       = Timetable.iloc[:, 4].to_numpy()

Times       = {}
Times['flight no']    =  Flight_num
Start_h     =  np.zeros(len(Flight_num))
Start_min   =  np.zeros(len(Flight_num))

End_h       =  np.zeros(len(Flight_num))
End_min     =  np.zeros(len(Flight_num))


for i in range(len(Flight_num)):
     t_start = [int(i) for i in (T_start[i].split(":",3))]
     t_end   = [int(i) for i in (T_end[i].split(":",3))]

     Start_h[i]    = t_start[0]
     Start_min[i]  = t_start[1]

     End_h[i]      = t_end[0]
     End_min[i]    = t_end[1]

Times['Start_h']    =  Start_h
Times['Start_min']  =  Start_min
Times['End_h']    =  End_h
Times['End_min']  =  End_min


Flight_time = ((End_h - Start_h) * 60 + End_min - Start_min) / 60  # flight time in hours

Cost = np.ones(len(Flights_duty))

#for i in range(len(Flights_duty)):
#     Flight_cost = 0
#      for j in list(Flights_duty[i]):
         #print(j)
         #index = list(Flight_num).index(j)



