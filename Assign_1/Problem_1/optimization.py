from gurobipy import *
import demand
import demand_loadData as load
import demand_functions as funct
import demand_globalData as globals
import matplotlib.pyplot as plt
import numpy as np

demand.demandForecast()

airlineData  = globals.airlineData
networkData  = globals.networkData
aircraftData = ...

YearToAnalyze = '2020'

airlineData = airlineData[YearToAnalyze]
q = airlineData['demand']

airports_lst = np.array(networkData['city'])
numberOfAirports = len(airports_lst)

aircraft_lst = np.array(networkData['AC type'])
numberOfAirports = len(aircraft_lst)

g = np.ones(numberOfAirports)
g[airports_lst=='Paris'] = 0

CXk_lst = aircraft['CXk']


# Start modelling optimization problem
m = Model('Network and Fleet Development')
x = {}
w = {}
z = {}
ACk = {}

# Iterate over itineraries
for i in range(numberOfAirports):
    for j in range(numberOfAirports):
        origin = airports_lst[i]    # To check the current airport origin
        dest   = airports_lst[j]    # To check the current airport destionation

        distance = funct.calculateDistance(origin, dest)

        x[i,j] = m.addVar(obj = (5.9*distance**(-0.76) + 0.043)*distance ,lb=0, vtype=GRB.INTEGER)
        w[i,j] = m.addVar(obj = (5.9*distance**(-0.76) + 0.043)*distance ,lb=0, vtype=GRB.INTEGER)

        # Iterate over AC types
        for k in range(numberOfAircraft):
            aircraftType = aircraft_lst[k]  # To check the current aircraft type in the iteration

            CXk = CXk_lst[k]    # fixed operating cost
            cTk = cTk[i,j][k]   # time based costs
            cfk = ... * distance# fuel cost
            spk = spk_lst[k]    # speed of aircraft
            CLk = ...

            z[i,j] = m.addVar(obj = (0.7 + 0.3*g[i]*g[j]) * (CXk + cTk * distance/spk + cfk/1.5*distance), lb=0, vtype=GRB.INTEGER)
            ACk    = m.addVar(obj = CLk , lb=0, vtype=GRB.INTEGER)

m.update()
m.setObjective(m.getObjective(), GRB.MAXIMIZE)  # The objective is to maximize revenue

# Define constraints
for i in range(numberOfAirports):
    for j in range(numberOfAirports):
        origin = airports_lst[i]    # To check the current airport origin
        dest   = airports_lst[j]    # To check the current airport destionation


        m.addConstr(x[i,j] + w[i,j], GRB.LESS_EQUAL, q[i,j]) #C1
        m.addConstr(w[i, j], GRB.LESS_EQUAL, q[i,j] * g[i] * g[j]) #C2
        ...
        ...
        ...


m.update()
# m.write('test.lp')
# Set time constraint for optimization (5minutes)
# m.setParam('TimeLimit', 1 * 60)
# m.setParam('MIPgap', 0.009)
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


# Print out Solutions
print()
print("Frequencies:----------------------------------")
print()
for i in airports:
    for j in airports:
        if z[i,j].X >0:
            print(Airports[i], ' to ', Airports[j], z[i,j].X)