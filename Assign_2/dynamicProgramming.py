from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials
from Stage import Stage
from Route import Route
from RouteNode import RouteNode
import pickle
import operator


def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

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

routesList = []

while any(amountInFleet > 0 for amountInFleet in Fleet.amount.values()):
    aircraftProfits = {}
    stagesListList = {}
    for type, aircraft in Fleet.aircraftList.items():
        if Fleet.amount[type] > 0: # check if aircraft type has amount in fleet left
            print("Aircraft type:", type)
            stagesList = load_obj(type)
            stagesListList[type] = stagesList

            print("Dynamic programming starts now ...")
            # iterate over all stages starting from last stage
            for i in range(len(stagesList)):
                if i % 10 == 0:
                    print("Current stage number: ", len(stagesList) - i - 1)
                currentStage = stagesList[len(stagesList) - i - 1]

                # iterate over all nodes in current stage, current node is ORIGIN
                for IATA, currentNode in currentStage.nodesList.items():

                    origin = airportsList[IATA]
                    currentAirportDemand = Demand.data.loc[Demand.data['From'] == IATA]  # added
                    
                    verticeProfit = {}
                    verticeCargo  = {}
                    # iterate over all vertices of this node, which are the DESTINATIONS
                    for iterIATA, iterStageNumber in currentNode.vertices.items():

                        destination = airportsList[iterIATA]
                        bin_num     = currentStage.binNumber

                        # IMPLEMENT: check demand of origin, destination
                        OrigDestDemand = currentAirportDemand.loc[currentAirportDemand['To'] == destination.IATA].drop(['From','To'], axis=1)    # origin destination demand

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
                        # save cargo
                        verticeCargo[iterIATA]  = cargoFlow


                    # IMPLEMENT: find max profit vertex
                    # IMPLEMENT: assign node IATA, stage number and corresponding profit to currentNode (self.profit, self.nextNodeStage, self.nextNodeIATA)
                    if currentStage.stageNumber == len(stagesList)-1:
                        currentNode.profit = 0
                        currentNode.cargo  = c
                    else:
                        profit = max(verticeProfit.values())
                        nextNodeIATA = max(verticeProfit.items(), key=operator.itemgetter(1))[0]
                        nextNodeStage = currentNode.vertices[nextNodeIATA]
                        nextNodeCargo = verticeCargo[nextNodeIATA]             # cargo added

                        currentNode.profit = profit
                        currentNode.nextNodeIATA = nextNodeIATA
                        currentNode.nextNodeStage = nextNodeStage
                        currentNode.cargo         = nextNodeCargo              # cargo added


            # IMPLEMENT: assign profit for aircraft type
            print(stagesList[0].nodesList[Airports.HUB].profit)
            aircraftProfits[type] = stagesList[0].nodesList[Airports.HUB].profit

    if all(value <= 0 for value in aircraftProfits.values()): # if no aircraft type gives a profitable route, stop adding new aircraft
        break

    # IMPLEMENT: save aircraft route with highest profit
    # find highest profit value, corresponding aircraft type and stageList
    highestAircraftProfitValue = max(aircraftProfits.values())
    highestAircraftProfitType = max(aircraftProfits.items(), key=operator.itemgetter(1))[0]
    highestAircraftProfitStageList = stagesListList[highestAircraftProfitType]
    print("Saving aircraft route of aircraft type " + str(highestAircraftProfitType) + " with a profit of " + str(highestAircraftProfitValue))

    # create new route
    routeToBeAdded = Route(highestAircraftProfitType, highestAircraftProfitValue)

    # set stage counter at first stage and current airport at the hub
    currentRouteStageCounter = 0
    currentRouteNodeIATA = Airports.HUB

    while True:
        currentRouteStage = highestAircraftProfitStageList[currentRouteStageCounter]
        currentRouteStageNode = currentRouteStage.nodesList[currentRouteNodeIATA]
        # create RouteNode with current airport, time, and profit left
        currentRouteNode = RouteNode(currentRouteNodeIATA, currentRouteStage.time, currentRouteStageNode.profit, currentRouteStageNode.cargo)  #CARGO ADDED
        # add RouteNode to Route
        routeToBeAdded.addRouteNode(currentRouteNode)

        if currentRouteStageCounter == numberOfStages - 1:
            break

        currentRouteStageCounter = currentRouteStageNode.nextNodeStage
        currentRouteNodeIATA = currentRouteStageNode.nextNodeIATA

    # add Route to list of routes
    routesList.append(routeToBeAdded)


    # IMPLEMENT: remove aircraft used from fleet
    Fleet.amount[highestAircraftProfitType] -= 1

    save_obj(routesList,"routes")
    break                                                                                                               # remove***********************

    # IMPLEMENT: remove demand transported
    # IMPLEMENT: check if we do not transport more than the demand we have (the thing the lecturer talked about with the 20% demand)

    # go back to start of while loop, check if aircraft left in fleet. stops if no aircraft left in fleet