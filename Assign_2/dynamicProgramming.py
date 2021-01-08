from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials
from Stage import Stage
from Route import Route
from RouteNode import RouteNode
import pickle
import operator
import pandas as pd
from pandas import ExcelWriter
from math import floor


def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

Airports = Airports('airports.xlsx')
Demand = Demand('demand.xlsx')
Fleet = Fleet('fleet.xlsx')
Financials = Financials('airports.xlsx','fleet.xlsx')

airportsList = Airports.airportsList
demand = Demand.data

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
            print("\n Aircraft type:", type)
            stagesList = load_obj(type)
            stagesListList[type] = stagesList

            print("Dynamic programming starts now ...")
            # iterate over all stages starting from last stage
            for i in range(len(stagesList)):
                if i % 100 == 0:
                    print("Current stage number: ", len(stagesList) - i - 1)
                currentStage = stagesList[len(stagesList) - i - 1]

                # iterate over all nodes in current stage, current node is ORIGIN
                for IATA, currentNode in currentStage.nodesList.items():

                    origin = airportsList[IATA]
                    currentAirportDemand = demand.loc[demand['From'] == IATA]
                    
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
                            cargoFlow = max(0,flightDemand)

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
                        currentNode.cargo  = 0
                    else:
                        profit = max(verticeProfit.values())
                        nextNodeIATA = max(verticeProfit.items(), key=operator.itemgetter(1))[0]
                        nextNodeStage = currentNode.vertices[nextNodeIATA]
                        nextNodeCargo = verticeCargo[nextNodeIATA]             # cargo added

                        currentNode.profit = profit
                        currentNode.nextNodeIATA = nextNodeIATA
                        currentNode.nextNodeStage = nextNodeStage
                        currentNode.cargo         = nextNodeCargo              # cargo added

                    if currentNode.profit < 0 and origin.city == 'Paris':
                        print()


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
    print("Saving aircraft route of aircraft type " + str(highestAircraftProfitType) + " with a profit of " + str(highestAircraftProfitValue) + '\n')

    # create new route
    routeToBeAdded = Route(highestAircraftProfitType, highestAircraftProfitValue)

    # set stage counter at first stage and current airport at the hub
    currentRouteStageCounter = 0
    currentRouteNodeIATA = Airports.HUB

    while True:
        currentRouteStage = highestAircraftProfitStageList[currentRouteStageCounter]
        currentRouteStageNode = currentRouteStage.nodesList[currentRouteNodeIATA]
        # create RouteNode with current airport, time, and profit left
        currentRouteNode = RouteNode(currentRouteNodeIATA, currentRouteStage.time, currentRouteStageNode.profit, currentRouteStageNode.cargo, currentRouteStageNode.stageNumber, currentRouteStage.binNumber)  #CARGO ADDED
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

    # IMPLEMENT: remove demand transported
    # IMPLEMENT: check if we do not transport more than the demand we have (the thing the lecturer talked about with the 20% demand)
    routeFlights   = routeToBeAdded.routeNodesList
    usedDemand     = demand.copy()
    binFlightTime  = {}
    binCargo       = {}
    binErrorProfit = {}

    # iterate over each node of the found aircraft route
    for i in range(len(routeFlights)-1):
        currentNode = routeFlights[i]
        nextNode    = routeFlights[i+1]

        # Enter loop if there is cargo transported at current node
        if currentNode.cargo != 0:
            if currentNode.binNumber not in binFlightTime:
                binFlightTime[currentNode.binNumber] = [currentNode.IATA, nextNode.IATA]
            else:
                binFlightTime[currentNode.binNumber] = [binFlightTime[currentNode.binNumber],[currentNode.IATA, nextNode.IATA]]

            binCargo_Node = {}

            # Obtain demand data
            indices_OD     = (usedDemand['From'] == currentNode.IATA) & (usedDemand['To'] == nextNode.IATA)
            origDestDemand = usedDemand.loc[indices_OD].drop(['From','To'], axis=1)

            binFlightDemand         = float(origDestDemand.iloc[0, currentNode.binNumber])
            prevBinFlightDemand     = float(origDestDemand.iloc[0, currentNode.binNumber-1])
            prevPrevBinFlightDemand = float(origDestDemand.iloc[0, currentNode.binNumber-2])

            # remove flight demand from current flight bin demand
            newBinFlightDemand     = binFlightDemand - currentNode.cargo
            demand.loc[indices_OD] = demand.loc[indices_OD].replace(demand.loc[indices_OD].iloc[0,2+currentNode.binNumber], max(0,newBinFlightDemand)) 
            binCargo_Node[currentNode.binNumber] = binFlightDemand - max(0,newBinFlightDemand)
            
            if currentNode.cargo > binFlightDemand:
                # remove flight demand from -1 flight bin demand
                newPrevBinFlightDemand = prevBinFlightDemand - abs(newBinFlightDemand)
                demand.loc[indices_OD] = demand.loc[indices_OD].replace(demand.loc[indices_OD].iloc[0,2+currentNode.binNumber-1], max(0,newPrevBinFlightDemand))
                binCargo_Node[currentNode.binNumber-1] = prevBinFlightDemand - max(0,newPrevBinFlightDemand)

                if abs(newBinFlightDemand) > prevBinFlightDemand:
                    # remove flight demand from -2 flight bin demand
                    newPrevPrevBinFlightDemand = prevPrevBinFlightDemand - abs(newPrevBinFlightDemand)
                    demand.loc[indices_OD]     = demand.loc[indices_OD].replace(demand.loc[indices_OD].iloc[0,2+currentNode.binNumber-2], max(0,newPrevPrevBinFlightDemand))
                    binCargo_Node[currentNode.binNumber-2] = prevPrevBinFlightDemand - max(0,newPrevPrevBinFlightDemand)
                
                    if abs(newPrevBinFlightDemand) > prevPrevBinFlightDemand:
                        # Zou dit zijn wat de lecturer bedoelde met die uitzondering??? Dus dat je eindigt met een negatieve demand
                        print(f'Het gaat mis hier bij vlucht {currentNode.IATA} naar {nextNode.IATA}, bij bin {currentNode.binNumber}')
            
            binCargo[currentNode.binNumber] = binCargo_Node
            
            # Check condition that we transport more than the demand we have on the flight one bin prior to the current flight
            if currentNode.binNumber-1 in binFlightTime:    # Is there a flight in the previous bin?
                if [currentNode.IATA, nextNode.IATA] == binFlightTime[currentNode.binNumber-1]: # Does that flight have the same origin-destination as the current flight?
                    if currentNode.binNumber-1 in binCargo[currentNode.binNumber]:  # Does the current flight carry demand from the previous bin?
                        oldPrevBinDemand = usedDemand.loc[(usedDemand['From'] == binFlightTime[currentNode.binNumber-1][0]) & (usedDemand['To'] == binFlightTime[currentNode.binNumber-1][1])].iloc[0,2+currentNode.binNumber-1]    # What was the original demand at the previous bin?
                        totalPrevTransportedDemand = binCargo[currentNode.binNumber-1][currentNode.binNumber-1] + binCargo[currentNode.binNumber][currentNode.binNumber-1]  # How much demand is transported?
                        if totalPrevTransportedDemand > oldPrevBinDemand:  # Has there been transported more demand than available?
                            # obtain the cargo flow that cannot be transported
                            prevErrorCargo = abs(totalPrevTransportedDemand - oldPrevBinDemand)

                            origin      = binFlightTime[currentNode.binNumber-1][0]     # errorenous flight
                            destination = binFlightTime[currentNode.binNumber-1][1]     # errorenous flight
                            
                            # compute the profit that has to be removed for the errorenous flight
                            flightRevenue = Financials.calculateRevenue(airportsList[origin], airportsList[destination], prevErrorCargo)
                            flightCost    = Financials.calculateCost(airportsList[origin], airportsList[destination], highestAircraftProfitType)
                            errorFlightProfit = flightRevenue - flightCost

                            # Add flight note and corresponding profit that has to be removed
                            if currentNode.binNumber not in binErrorProfit:
                                binErrorProfit[currentNode] = errorFlightProfit
                            else:
                                binErrorProfit[currentNode] = [binErrorProfit[currentNode], errorFlightProfit]

            # check condition that we transport more than the demand we have on the flight two bins prior to the current flight
            if currentNode.binNumber-2 in binFlightTime:    # Is there a flight in the pre previous bin?
                if [currentNode.IATA, nextNode.IATA] == binFlightTime[currentNode.binNumber-2]: # Does that flight have the same origin-destination as the current flight?
                    if currentNode.binNumber-2 in binCargo[currentNode.binNumber]:  # Does the current flight carry demand from the pre previous bin?
                        oldPrevPrevBinDemand = usedDemand.loc[(usedDemand['From'] == binFlightTime[currentNode.binNumber-2][0]) & (usedDemand['To'] == binFlightTime[currentNode.binNumber-2][1])].iloc[0,2+currentNode.binNumber-2]    # What was the original demand at the previous bin?
                        totalPrevPrevTransportedDemand = binCargo[currentNode.binNumber-2][currentNode.binNumber-2] + binCargo[currentNode.binNumber][currentNode.binNumber-2]  # How much demand is transported?
                        if totalPrevPrevTransportedDemand > oldPrevPrevBinDemand:  # Has there been transported more demand than available?
                            # obtain the cargo flow that cannot be transported
                            prevPrevErrorCargo = abs(totalPrevPrevTransportedDemand - oldPrevPrevBinDemand)

                            origin      = binFlightTime[currentNode.binNumber-1][0]     # errorenous flight
                            destination = binFlightTime[currentNode.binNumber-1][1]     # errorenous flight
                            
                            # compute the profit that has to be removed for the errorenous flight
                            flightRevenue = Financials.calculateRevenue(airportsList[origin], airportsList[destination], prevPrevErrorCargo)
                            flightCost    = Financials.calculateCost(airportsList[origin], airportsList[destination], highestAircraftProfitType)
                            errorFlightProfit = flightRevenue - flightCost

                            # Add flight note and corresponding profit that has to be removed
                            if currentNode.binNumber not in binErrorProfit:
                                binErrorProfit[currentNode] = errorFlightProfit
                            else:
                                binErrorProfit[currentNode] = [binErrorProfit[currentNode], errorFlightProfit]
        
    if len(binErrorProfit) >= 1:
        print(f'To much demand is transported on the flight in the following bin, resulting in the following reduction in profit: {binErrorProfit}')
    else:
        print('No errorenous cargo flow present')
                    
    # go back to start of while loop, check if aircraft left in fleet. stops if no aircraft left in fleet

save_obj(routesList,"routesList")

with ExcelWriter('output/routes.xlsx') as writer:
    for i, rte in enumerate(routesList):
        aircraftNumString = 'num' + str(i) + '_' + rte.aircraftType
        df = pd.DataFrame(columns=['Departure Time', 'Route', 'Arrival Time', 'Cargo', 'Profit'])

        rteNodesList = rte.routeNodesList

        for i in range(len(rteNodesList) - 1):
            origin = rteNodesList[i].IATA
            destination = rteNodesList[i + 1].IATA
            if origin != destination:
                depTime = rteNodesList[i].time
                depTimeDays = floor(depTime/24) + 1
                depTimeHours = int(depTime - depTimeDays*24)
                depTimeMinutes = round(((depTime - depTimeDays*24) % 1) * 60)
                depTimeString = 'Day ' + str(depTimeDays) + ' - ' + str(depTimeHours) + ' h ' + str(depTimeMinutes)

                arrTime = rteNodesList[i + 1].time
                arrTimeDays = floor(arrTime/24) + 1
                arrTimeHours = int(arrTime - arrTimeDays*24)
                arrTimeMinutes = round(((arrTime - arrTimeDays*24) % 1) * 60)
                arrTimeString = 'Day ' + str(arrTimeDays) + ' - ' + str(arrTimeHours) + ' h ' + str(arrTimeMinutes)

                cargo = rteNodesList[i].cargo
                profit = rteNodesList[i].profitLeft - rteNodesList[i + 1].profitLeft
                df.loc[i] = [depTimeString, origin+' - '+destination, arrTimeString, cargo, profit]

        df.to_excel(writer, sheet_name = aircraftNumString, index= False)
