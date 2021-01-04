from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials
from Stage import Stage
import pickle
import operator
from Node_profit import Node_profit


def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

Airports = Airports()
Demand = Demand()
Fleet = Fleet()
Financials = Financials()

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

numberOfStages = int(TOTAL_HOURS*60 / STAGE_RESOLUTION + 1)

while all(amountInFleet > 0 for amountInFleet in Fleet.amount.values()):
    profit = {}
    for type, aircraft in Fleet.aircraftList.items():
        if Fleet.amount[type] > 0: # check if aircraft type has amount in fleet left
            stagesList = load_obj(type)

            print("Dynamic programming starts now ...")
            # iterate over all stages starting from last stage
            for i in range(len(stagesList)):
                print("Current stage number: ", len(stagesList) - i - 1)
                currentStage = stagesList[len(stagesList) - i - 1]

                # iterate over all nodes in current stage, current node is ORIGIN
                for IATA, currentNode in currentStage.nodesList.items():

                    origin = airportsList[IATA]
                    currentAirportDemand = Demand.data.loc[Demand.data['From'] == IATA]  # added
                    
                    verticeProfit = {}
                    # iterate over all vertices of this node, which are the DESTINATIONS
                    for iterIATA, iterStageNumber in currentNode.vertices.items():

                        destination = airportsList[iterIATA]
                        bin_num     = currentStage.binNumber

                        # IMPLEMENT: check demand of origin, destination
                        OrigDestDemand = currentAirportDemand.loc[currentAirportDemand['To'] == destination.IATA].drop(['From','To'], axis=1)    # origin destionation demand

                        directDemand = float( OrigDestDemand.iloc[0,bin_num] )
                        prevDemand   = float( OrigDestDemand.iloc[0,bin_num-1] )
                        pprevDemand  = float( OrigDestDemand.iloc[0,bin_num-2] )
                        flightDemand = directDemand + DEMAND_CAPTURE_PREVIOUS*(prevDemand + pprevDemand)

                        flightCapacity = Fleet.aircraftList[type].capacity

                        if flightDemand > flightCapacity:
                            cargoFlow = flightCapacity
                        else:
                            cargoFlow = flightDemand

                        # IMPLEMENT: calculate profit of vertices
                        flightRevenue = Financials.calculateRevenue(origin, destination, cargoFlow)
                        flightCost    = Financials.calculateCost(origin, destination, type) if origin != destination else 0
                        flightProfit  = flightRevenue - flightCost
                        oldProfit     = stagesList[iterStageNumber].nodesList[iterIATA].profit 
                        totalProfit   = oldProfit + flightProfit

                        verticeProfit[iterIATA] = totalProfit

                    # IMPLEMENT: find max profit vertex
                    # IMPLEMENT: assign node IATA, stage number and corresponding profit to currentNode (self.profit, self.nextNodeStage, self.nextNodeIATA)
                    if currentStage.stageNumber == len(stagesList)-1:
                        currentNode.profit = 0
                        currentNode.nextNodeIATA = Airports.HUB
                        currentNode.nextNodeStage = Airports.HUB
                    else:
                        profit = max(verticeProfit.values())
                        nextNodeIATA = max(verticeProfit.items(), key=operator.itemgetter(1))[0]
                        nextNodeStage = currentNode.vertices[nextNodeIATA]

                        currentNode.profit = profit
                        currentNode.nextNodeIATA = nextNodeIATA
                        currentNode.nextNodeStage = nextNodeStage
                        if flightProfit > 0:
                            print(flightProfit,totalProfit)

            # CODE BELOW THIS STILL TO BE IMPLEMENTED ================
            profit[type] = 0 # IMPLEMENT: find total profit for aircraft type
            for i in range(len(stagesList)):
                currentStage = stagesList[len(stagesList) - i - 1]
                for IATA, currentNode in currentStage.nodesList.items():
                    profit[type] += currentNode.profit


    if not all(value > 0 for value in profit.values()): # if no aircraft type gives a profitable route, stop adding new aircraft
        break

    # IMPLEMENT: save aircraft route
    # IMPLEMENT: remove aircraft used from fleet

    Fleet.amount[type] = Fleet.amount[type] -1

    # IMPLEMENT: remove demand transported


    # go back to start of while loop, check if aircraft left in fleet. stops if no aircraft left in fleet