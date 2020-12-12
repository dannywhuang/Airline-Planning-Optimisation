from gurobipy import *
import demand
import demand_loadData as load
import demand_functions as funct
import demand_globalData as globals
import aircraft_loadData as aircraftLoad
from formatFunctions import formatOutput
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BT = 10*7  # 10 hour block time per day (use value for a week)
f = 1.42   # 1.42 USD/gallon to EUR/gallon # usd price is used to calibrate function

demand.demandForecast()

airlineData  = globals.airlineData
networkData  = globals.networkData
aircraftData = aircraftLoad.loadData()



YearToAnalyze = '2020'

airlineData = airlineData[YearToAnalyze]
q = airlineData['demand']


print(aircraftData.loc['Speed'].iloc[0])

airports_lst = np.array(networkData['city'])
airportsRunway_lst = np.array(networkData['rnw'])
airports = range(len(airports_lst))

g = np.ones(len(airports_lst))
g[airports_lst=='Paris'] = 0
print(g)

aircraft = range(len(aircraftData.columns))


m = Model('Network and Fleet Development')
# Decision variables
x = {}
w = {}
z = {}
AC = {}
# Other variables
s = {}
sp = {}
TAT = {}
R = {}
RunAC = {}
# Add variables that are not in the objective function
for k in aircraft:
    singleAircraftData = aircraftData.iloc[:, k]
    s[k] = singleAircraftData['Seats']
    sp[k] = singleAircraftData['Speed']
    TAT[k] = singleAircraftData['Average TAT']/60 #from minutes to hours
    R[k] = singleAircraftData['Maximum range']
    RunAC[k] = singleAircraftData['Runway required']


# Add variables that are in the objective function as well
for i in airports:
    for j in airports:
        if i!=j:
            origin = airports_lst[i]    # To check the current airport origin
            dest   = airports_lst[j]    # To check the current airport destination

            distance = funct.calculateDistance(origin, dest)

            x[i,j] = m.addVar(obj = (5.9*distance**(-0.76) + 0.043)*distance ,lb=0, vtype=GRB.INTEGER, name="x[%s,%s]" % (i, j))
            w[i,j] = m.addVar(obj = (5.9*distance**(-0.76) + 0.043)*distance ,lb=0, vtype=GRB.INTEGER, name="w[%s,%s]" % (i, j))

            # Iterate over AC types
            for k in aircraft:
                singleAircraftData = aircraftData.iloc[:, k]  # To check the current aircraft type in the iteration

                # CXk = aircraftData.loc[ '' ,  ]     # fixed operating cost
                cTk = singleAircraftData['Time cost parameter']   # time based costs
                cfk = singleAircraftData['Fuel cost parameter']   # fuel cost
                spk = singleAircraftData['Speed']                 # speed of aircraft
                CLk = singleAircraftData['Weekly lease cost']
                CXk = singleAircraftData['Fixed operating cost']

                z[i,j,k] = m.addVar(obj = -(0.7 + 0.3*g[i]*g[j]) * (CXk + cTk * distance/spk + cfk*f/1.5*distance), lb=0, vtype=GRB.INTEGER, name="z[%s,%s,%s]" % (i, j, k))
                AC[k]    = m.addVar(obj = -CLk , lb=0, vtype=GRB.INTEGER, name="AC[%s]" % (k))



m.update()
m.setObjective(m.getObjective(), GRB.MAXIMIZE)  # The objective is to maximize revenue

m.addConstrs(x[i,j] + w[i,j] <= q[i,j] for i in airports for j in airports if i!=j)
m.addConstrs(w[i,j] <= q[i,j]*g[i]*g[j] for i in airports for j in airports if i!=j)
m.addConstrs(x[i,j] + quicksum(w[i,m]*(1-g[j]) for m in airports if m!=i) + quicksum(w[m,j]*(1-g[i]) for m in airports if m!=j) <= quicksum(z[i,j,k]*s[k]*globals.LF for k in aircraft) for i in airports for j in airports if i!=j)
m.addConstrs(quicksum(z[i,j,k] for j in airports if i!=j) - quicksum(z[j,i,k] for j in airports if i!=j) == 0 for i in airports for k in aircraft)
m.addConstrs(quicksum(quicksum((funct.calculateDistance(i, j)/sp[k]+ (TAT[k]) *(1.5-0.5*g[j]))*z[i, j, k] for j in airports if i!=j) for i in airports)  <= BT*AC[k]  for k in aircraft)
m.addConstrs(z[i,j,k] <= (10000 if funct.calculateDistance(i, j) <= R[k] else 0) for i in airports for j in airports for k in aircraft if i!=j)
m.addConstrs(z[i,j,k] <= (10000 if ((RunAC[k] <= airportsRunway_lst[i]) and (RunAC[k] <= airportsRunway_lst[j])) else 0) for i in airports for j in airports for k in aircraft if i!=j)



#
# # Define constraints
# for i in range(numberOfAirports):
#     for j in range(numberOfAirports):
#         if i!=j:
#             origin = airports_lst[i]    # To check the current airport origin
#             dest   = airports_lst[j]    # To check the current airport destination
#             distance = funct.calculateDistance(origin, dest)
#
#             m.addConstr(x[i,j] + w[i,j] <= q[i,j], name="C1") # C1
#             m.addConstr(w[i, j] <= q[i,j] * g[i] * g[j], name="C2") # C2
#             for k in range(numberOfAircraft):
#                 singleAircraftData = aircraftData.iloc[:, k]  # To check the current aircraft type in the iteration
#
#                 m.addConstr(x[i, j] + quicksum(w[i, j]*(1-g[j]) for j in range(numberOfAirports) if i!=j) + quicksum(w[i, j]*(1-g[i]) for i in range(numberOfAirports) if i!=j) <= quicksum(z[j, i, k]*s[k]*globals.LF for k in range(numberOfAircraft)), name="C3")  # C3
#
#                 m.addConstr(quicksum(z[i, j, k] for j in range(numberOfAirports) if i!=j) <= quicksum(z[j, i, k] for j in range(numberOfAirports) if i!=j), name="C4")  # C4
#
#                 m.addConstr(quicksum(quicksum((distance / sp[k] + TAT[k]*(1.5-0.5*g[j])) * z[i, j, k] for i in range(numberOfAirports)if i!=j) for j in range(numberOfAirports) if i!=j) <= BT * AC[k], name="C5")  # C5
#
#                 m.addConstr(z[i,j,k] <= (10000 if distance <= R[k] else 0), name="C6")  # c6
#
#                 m.addConstr(z[i,j,k] <= (10000 if ((RunAC[k] <= airportsRunway_lst[i]) and (RunAC[k] <= airportsRunway_lst[j])) else 0), name="C7")   # c7

if __name__ == '__main__':
    m.update()
    # m.write('test.lp')
    # Set time constraint for optimization (5minutes)
    # m.setParam('TimeLimit', 1 * 60)
    # m.setParam('MIPgap', 0.009)
    # m.computeIIS()
    # m.write("IIS.ilp")
    m.optimize()
    # m.write("testout.sol")
    status = m.status

    if status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')

    elif status == GRB.Status.OPTIMAL or True:
        f_objective = m.objVal
        print('***** RESULTS ******')
        print('\nObjective Function Value: \t %g' % f_objective)

    elif status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
        
    formatOutput(m)

    # Print out Solutions
    print()
    print("Frequencies:----------------------------------")
    print()
    ask = np.ones((4*len(airports)**2,4))
    p = 0
    for i in airports:
        for j in airports:
            origin = airports_lst[i]    # To check the current airport origin
            dest   = airports_lst[j]    # To check the current airport destination
            distance = funct.calculateDistance(origin, dest)
            for k in aircraft:
                if i!= j:
                    if z[i,j,k].X >0:
                        ask[p,3] = s[k]*distance
                        ask[p, 0] =  i
                        ask[p, 1] =  j
                        ask[p, 2] = k
                        print(airports_lst[i], ' to ', airports_lst[j], z[i,j,k].X,k)
                        p = p+1


    # for var in m.getVars():
    #     if var.x:
    #         print('%s %f' % (var.varName, var.x))




