from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Financials import Financials
from Stage import Stage
import pickle
from Node_profit import Node_profit


def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

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

numberOfStages = int(TOTAL_HOURS*60 / STAGE_RESOLUTION + 1)



while all(amountInFleet > 0 for amountInFleet in Fleet.amount.values()):
    profit = {}
    for type, aircraft in Fleet.aircraftList.items():
        if Fleet.amount[type] > 0: # check if aircraft type has amount in fleet left
            stagesList = load_obj(type)

            print("Dynamic programming starts now...")
            # iterate over all stages starting from last stage
            for i in range(len(stagesList)):
                print("Current stage number: ", i)
                currentStage = stagesList[len(stagesList) - i - 1]

                # iterate over all nodes in current stage, current node is ORIGIN
                for IATA, currentNode in currentStage.nodesList.items():

                    currentAirportDemand = Demand.data.loc[Demand.data['From'] == IATA]  # added

                    currentNodeProfit = {}
                    # iterate over all vertices of this node, which are the DESTINATIONS
                    for iterIATA, iterStageNumber in currentNode.vertices.items():

                        # IMPLEMENT: check demand of origin, destination
                        cap = Fleet.aircraftList[type].capacity
                        destination = currentAirportDemand[currentAirportDemand['To'] == iterIATA]
                        bin_num     = currentStage.binNumber
                        demand      = float(destination[bin_num])

                        if cap >= demand  and bin_num >1:                               # check other constraints
                            demand_1before = float(destination[bin_num - 1])
                            demand_2before = float(destination[bin_num - 2])
                            cap_left = cap-demand
                            DEMAND_CAPTURE_MAX = DEMAND_CAPTURE_PREVIOUS*(demand_1before+demand_2before)
                            Capture = cap_left if DEMAND_CAPTURE_MAX-cap_left > 0 else DEMAND_CAPTURE_MAX
                            cargo = demand + Capture
                        else:
                            cargo = cap

                        # IMPLEMENT: calculate profit of vertices
                        revenue = Financials.calculateRevenue(IATA,iterIATA,cargo)
                        cost    = Financials.calculateCost(IATA,iterIATA,type)
                        profit  = revenue-cost
                        # note: leasing cost should not be considered
                        currentNodeProfit[IATA,iterIATA] = Node_profit(type,IATA,iterIATA,profit,bin_num,iterStageNumber,cargo)

                        pass # remove pass when finished

                    # IMPLEMENT: find max profit vertex
                    prof = 0
                    for vertex, node_prof in currentNodeProfit.items():
                       if node_prof.profit > prof:
                           vertex_max = vertex
                           currentNode.profit        = node_prof.profit
                           currentNode.nextNodestage = node_prof.stage-1
                           currentNode.nextNodeIATA  = node_prof.destination

                    # IMPLEMENT: assign node IATA, stage number and corresponding profit to currentNode (self.profit, self.nextNodeStage, self.nextNodeIATA)

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