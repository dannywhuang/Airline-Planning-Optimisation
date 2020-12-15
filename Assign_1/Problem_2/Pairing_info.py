import numpy as np
import pandas as pd
import ast
from objectLoader import load_obj


File2 = '2_Duty_Periods_Group_34.xlsx'

Duty_period = pd.read_excel(File2, usecols='A:B', converters={'column_name': eval})

Flights_duty     =  Duty_period.iloc[:, 1].apply(ast.literal_eval)


pairings = load_obj('pairing')
cost = load_obj('cost')
hotelcost = load_obj('hotel_cost')
flightcost = load_obj('flight_cost')
fixedcost = load_obj('fixed_cost')
durationNoBrief = load_obj('duration_no_brief')
durationWithBrief = load_obj('duration_with_brief')

df = pd.DataFrame(columns=['pairing', 'number of flights', 'duration', 'fixed costs', 'flight costs', 'hotel costs', 'total costs'])

sumCost = 0

for p in pairings:
    q = int(p)
    df.loc[q] = [str(q), len(Flights_duty[q]), durationWithBrief[q], fixedcost, flightcost[q], hotelcost[q], cost[q]]
    sumCost += cost[q]

df.to_excel('Pairing_info.xlsx')
print(sumCost)