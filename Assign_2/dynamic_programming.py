from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials
from Stage import Stage

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
TOTAL_HOURS = 120

numberOfStages = int(120*60 / 6 + 1)
stagesList = [None]*numberOfStages

while all(amountInFleet > 0 for amountInFleet in Fleet.amount.values()):
    profit = {}
    for type, aircraft in Fleet.aircraftList.items():
        if Fleet.amount[type] > 0: # check if aircraft type has amount in fleet left

            # create last stage and add HUB node
            airportHUB = airportsList[Airports.HUB]
            lastStage = Stage(TOTAL_HOURS)
            lastStage.addNode(airportHUB)
            stagesList[-1] = lastStage

            # create other stages
            for i in range(1, numberOfStages):
                stageTime = TOTAL_HOURS-i*0.1
                newStage = Stage(stageTime)
                stagesList[numberOfStages - i - 1] = newStage
                # for each stage create airport nodes
                newStage.addNode(airportHUB)
                for IATA, airport in Airports.airportsList.items():
                    # only add airport nodes to stage that have the runway required

                    if airport.runway > aircraft.runwayRequired:
                        # only add airport if you can still reach HUB before end of day 5
                        if (Airports.calculateDistance(airport, airportHUB)/aircraft.speed + aircraft.TAT/60) < TOTAL_HOURS-stageTime:
                            newStage.addNode(airport)

            # IMPLEMENT: do dynamic programming


            profit[type] = 0 # find total profit for aircraft type


    if not all(value > 0 for value in profit.values()): # if no aircraft type gives a profitable route, stop adding new aircraft
        break

    # IMPLEMENT: save aircraft route
    # IMPLEMENT: remove aircraft used from fleet
    # IMPLEMENT: remove demand transported

    # go back to start of while loop, check if aircraft left in fleet. stops if no aircraft left in fleet