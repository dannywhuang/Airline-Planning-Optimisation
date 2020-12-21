from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials

Airports = Airports()
Demand = Demand()
Fleet = Fleet()

airportsList = Airports.airportsList


BINS_0AM_4AM = [0,6,12,18,24]
BINS_4AM_8AM = [1,7,13,19,25]
BINS_8AM_12PM = [2,8,14,20,26]
BINS_12PM_4PM = [3,9,15,21,27]
BINS_4PM_8PM = [4,10,16,22,28]
BINS_8PM_12AM = [5,11,17,23,29]

STAGE_RESOLUTION = 6 # 6 minutes
DEMAND_CAPTURE_PREVIOUS = 0.20 # 20% of previous two bins can capture

while all(amountInFleet > 0 for amountInFleet in Fleet.amount.values()):
    profit = {}
    for aircraft in Fleet.aircraftList:
        if Fleet.amount[aircraft.type] > 0: # check if aircraft type has amount in fleet left
            # IMPLEMENT: do dynamic programming
            profit[aircraft.type] = 0 # find profit for aircraft type


    if not all(value > 0 for value in profit.values()): # if no aircraft type gives a profitable route, stop adding new aircraft
        break

    # IMPLEMENT: save aircraft route
    # IMPLEMENT: remove aircraft used from fleet
    # IMPLEMENT: remove demand transported

    # go back to start of while loop, check if aircraft left in fleet. stops if no aircraft left in fleet