import numpy as np
import pandas as pd
from datetime import datetime
import ast
from gurobipy import *
from objectLoader import load_obj
import collections
import os
import glob
import time
import matplotlib.pyplot as plt

def graph(x,y):
    fig, ax = plt.subplots()
    plt.suptitle("Objective function value for each column generation iteration",fontsize=16)
    plt.rcParams["font.size"] = "12"
    plt.rcParams["axes.labelsize"] = "12"
    ax.set_ylabel('Objective [MU]', fontsize=12.0)
    ax.set_xlabel('Iteration [-]', fontsize=12.0)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.tick_params(axis='both', which='minor', labelsize=12)

    plt.plot(x, y)
    plt.grid()
    plt.legend()
    ax.autoscale()
    plt.show()

    return

# clear log files
files = glob.glob('logs/*')
for f in files:
    os.remove(f)

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

Flights_duty    =  Duty_period.iloc[:, 1].apply(ast.literal_eval)

Flight_num  = Timetable.iloc[:, 0].to_numpy()
Origin      = Timetable.iloc[:, 1].to_numpy()
T_start     = Timetable.iloc[:, 3].to_numpy()
T_end       = Timetable.iloc[:, 4].to_numpy()

# define set of P pairings and set of F flights
P = range(len(Flights_duty))
F = range(len(Flight_num))


# parameters cost and dfp
cost = load_obj('cost')
dpf = load_obj('dpf')
print("Should be 1: ", dpf[33441, 133]) # verification, should give 1
print("Should be 0: ", dpf[33440, 133]) # verification, should give 0

# load model


# current pairings in the model
pCurrent = np.array([], dtype='int')
objectiveValues = np.array([])

# add pairings to the model that have only 1 flight
for p in P:
    if len(Flights_duty[p]) == 1:
        pCurrent = np.append(pCurrent, int(p))

# column generation
iterationCount = 1
start_time = time.time()
while True:
    print("\n")
    print("Iteration", iterationCount)
    m = Model('Column Generation Problem')
    # decision variable x
    x = {}
    for p in pCurrent:
        x[p] = m.addVar(obj=cost[p], vtype=GRB.CONTINUOUS, name="x[%s]" % (p))

    m.update()

    m.setObjective(m.getObjective(), GRB.MINIMIZE)  # The objective is to minimize crew cost
    m.setParam("LogFile", 'logs/iteration' + str(iterationCount))
    # add constraints
    m.addConstrs(quicksum(dpf[p, f]*x[p] for p in pCurrent) == 1 for f in F)
    m.update()

    # optimize
    m.optimize()

    # write column generation solution to gurobi file
    file = open('logs/iteration' + str(iterationCount), 'a')
    file.write('\nSolution')
    for var in m.getVars():
        if var.x:
            file.write('%s %f \n' % (var.varName, var.x))
    file.close()

    # get dual variables
    dualPi = {}
    for count,constr in enumerate(m.getConstrs()):
        dualPi[count] = constr.Pi

    # compute slack for each pairing not in the model
    slack = {}
    for p in P:
        if p not in pCurrent:
            positive = 0
            for f in F:
                positive += dpf[p, f] * dualPi[f]
            negative = -cost[p]
            slack[p] = positive + negative

    # sort slack from highest slack to lowest
    sortedSlack = sorted(slack.items(), key=lambda x: x[1], reverse=True)

    # add 50 pairings with best slack, if slack  > 0
    for i in range(50):
        if sortedSlack[i][1] > 0:
            # print("Iteration " + str(iterationCount) + ", pairing: " + str(sortedSlack[i][0]) + ", slack: " + str(sortedSlack[i][1]))
            pCurrent = np.append(pCurrent, sortedSlack[i][0])
        else:
            break

    # add objective value to array
    objectiveValues = np.append(objectiveValues, m.objVal)
    iterationCount += 1
    # check if all 6 iterations have a difference of less than 0.001 MU, if yes break
    if len(objectiveValues) >= 5:
        difference = np.diff(objectiveValues)
        if all(abs(i) <= 0.001 for i in difference[-5:]):
            break

graph(range(1,iterationCount),objectiveValues)

print("\n")
print("The column generation algorithm took")
print("--- %s seconds ---" % (time.time() - start_time))
# now solve the actual problem with binary variables
print("\n")
print("Amount of pairings: ",len(pCurrent))
m = Model('Crew Pairing Problem')
x2 = {}

for p in pCurrent:
    x2[p] = m.addVar(obj=cost[p], vtype=GRB.BINARY, name="x[%s]" % (p))

m.update()
m.setParam("LogFile", 'logs/final')
m.setObjective(m.getObjective(), GRB.MINIMIZE)  # The objective is to minimize crew cost

# add constraints
m.addConstrs(quicksum(dpf[p, f] * x2[p] for p in pCurrent) == 1 for f in F)
m.update()

# optimize
m.optimize()

file = open('logs/final', 'a')
file.write('\nSolution')
for var in m.getVars():
    if var.x:
        file.write('%s %f \n' % (var.varName, var.x))
file.close()

for var in m.getVars():
    if var.x:
        print('%s %f' % (var.varName, var.x))

flight_check = np.array([])
for i in P:
    if i in x2 and x2[i].x:
        lis = Flights_duty[i]
        for q in range(len(lis)):
            flight_check = np.append(flight_check,lis[q])

print("Length of flights covered: ",len(flight_check))
print("Length of flights planned: ",len(Flight_num))
print("Are all flights covered? ", collections.Counter(flight_check) == collections.Counter(Flight_num))
print("Are all flights covered double check? ", all(i in flight_check for i in Flight_num))

