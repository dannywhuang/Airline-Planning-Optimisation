import pickle

def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)



from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Stage import Stage

Airports = Airports()
Demand = Demand()
Fleet = Fleet()

airportsList = Airports.airportsList

STAGE_RESOLUTION = 6 # 6 minutes
TOTAL_HOURS = 120

numberOfStages = int(TOTAL_HOURS*60 / STAGE_RESOLUTION + 1)


for type, aircraft in Fleet.aircraftList.items():
    print("Aircraft type: ", type)
    stagesList = [None] * numberOfStages
    # create last stage and add HUB node
    airportHUB = airportsList[Airports.HUB]
    lastStage = Stage(TOTAL_HOURS)
    lastStage.addNode(airportHUB)
    stagesList[-1] = lastStage

    print("Creating stages and nodes...")
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

    # start creating vertices
    print("Creating vertices...")
    # iterate over all stages starting from last stage
    for i in range(len(stagesList)):
        currentStage = stagesList[len(stagesList) - i - 1]

        # iterate over all nodes in current stage
        for IATA, currentNode in currentStage.nodesList.items():

            # find all demand entries that depart from this node
            currentAirportDemand = Demand.data.loc[Demand.data['From'] == IATA]

            # iterate over all possible destinations from current airport node
            for index, row in currentAirportDemand.iterrows():
                currentDestinationIATA = row['To']

                # iterate over all stages after current stage
                for j in range(i):
                    iterStage = stagesList[len(stagesList) - i + j]
                    stageTimeDifference = iterStage.time - currentStage.time

                    if currentDestinationIATA in iterStage.nodesList:
                        iterNode = iterStage.nodesList[currentDestinationIATA]
                        totalTravelTime = Airports.calculateDistance(currentNode.airport, iterNode.airport)/aircraft.speed + aircraft.TAT/60
                        if totalTravelTime < stageTimeDifference or currentNode.airport.IATA == iterNode.airport.IATA:
                            currentNode.vertices.append(iterNode)
                            break
    save_obj(stagesList, type)