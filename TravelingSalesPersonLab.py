import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import pandas as pd
import matplotlib.pyplot as plt

#This is the entry point for the default solver which just finds a valid random tour.
def defaultRandomTour(self, time_allowance=60.0):
    results = pd.DataFrame(columns=["Time", "Score"])
    cities = self._scenario.getCities()
    ncities = len(cities)
    foundTour = False
    count = 0
    bssf = None
    start_time = time.time()

    #continue looping until we find a path and time runs out
    while not foundTour and time.time() - start_time < time_allowance:
        # create a random permutation
        perm = np.random.permutation(ncities)
        route = []

        # Now build the route using the random permutation
        for i in range(ncities):
            route.append(cities[perm[i]])
        bssf = TSPSolution(route)
        count += 1

        if bssf.cost < np.inf:
            # Found a valid route
            foundTour = True
    #setting our initial values
    end_time = time.time()
    results['cost'] = bssf.cost if foundTour else math.inf
    results['time'] = end_time - start_time
    results['count'] = count
    results['soln'] = bssf
    results['max'] = None
    results['total'] = None
    results['pruned'] = None
    return results


#This is the entry point for the greedy solver
def greedy(self, time_allowance=60.0):
    start_time = time.time()
    results = {}
    cities = self._scenario.getCities()
    cities = self._scenario.getCities()
    ncities = len(cities)
    foundTour = False
    count = 1
    bssf = None

    masterMatrix = self.first_matrix(cities)

    for startingSpot in range(0,ncities):  # if we can't find a path from our current starting point, just move to next starting point
        #Continue looking while we don't have a path and while we still have time left
        if foundTour != True and time.time() - start_time < time_allowance:
            currentSpot = copy.deepcopy(startingSpot)
            path = []
            cityMatrix = np.array(copy.deepcopy(masterMatrix))
            cityMatrix[:, 0] = math.inf

            #keeping track of the paths
            for city in cities:
                path.append(cities[currentSpot])

                min_row = np.min(cityMatrix, axis=1)
                result = np.all(min_row == min_row[0])

                if result and len(path) == ncities:  # break out if all min values are inf, we know we can't find a sol here now.
                    bssf = TSPSolution(path)
                    if bssf.cost < np.inf:  # only a good solution if the cost isn't inf
                        #we have found a solution
                        foundTour = True
                        results = self.return_results(path, start_time)
                        return results

                #setting new values
                min_row_index = np.argmin(cityMatrix, axis=1)
                min_spot = min_row_index[currentSpot]
                cityMatrix[currentSpot][min_spot] = math.inf
                cityMatrix[:, min_spot] = math.inf
                currentSpot = min_spot

    #Return results to the GUI
    results = self.return_results(path, start_time)
    return results


#Returning the results back to the GUI to graph them
def return_results(self, path, start_time):
    results = {}
    bssf = TSPSolution(path)
    print("bssf is equel to " + str(bssf.cost))

    end_time = time.time()
    results['cost'] = bssf.cost
    results['time'] = end_time - start_time
    results['count'] = 1
    results['soln'] = bssf
    results['max'] = None
    results['total'] = None
    results['pruned'] = None
    return results


#This is the entry point for the branch-and-bound algorithm
def branchAndBound(self, time_allowance=60.0):
    #setting initial values
    results = {}
    cities = self._scenario.getCities()
    default = self.greedy()
    lowest_cost = default['cost']
    num_updates = 0
    max_heap_len = 1
    pruned = 0
    num_states = 0
    bssf = default['soln']

    heap = []
    heapq.heapify(heap)

    # making the first matrix and reducing it
    masterMatrix = self.first_matrix(cities)
    reduction = self.ReduceMatrix(masterMatrix, cities)
    masterMatrix = reduction[0]
    bound = reduction[1]

    matrixCopy = np.array(copy.deepcopy(masterMatrix)) #copy so we are not changing the orginal in case the found path is not better.
    matrixCopy[:, 0] = math.inf
    currentNode = node(current_city=cities[0], RCM=matrixCopy, bound=bound,
                       rem_cities=None, path=[cities[0]])
    heapq.heappush(heap, (currentNode.score, currentNode))  # adding the first node onto heap

    # Begining the process of looking for a path
    start_time = time.time()
    #Continue while we still have something on our heap and while we still have time left.
    while len(heap) > 0 and time.time() - start_time < time_allowance:
        currentNode = heap[0][1]
        heap.pop(0)  # pop the top node off
        if currentNode.bound > lowest_cost:  # checking if node needs to be pruned
            pruned += 1
        else:
            currentRCM = np.array(currentNode.RCM)  # setting the RCM until the next node is picked
            i = currentNode.current_city._index
            for j in range(0,len(cities)):  # looping thru all the other things it could be connected to that haven't been visited
                if currentRCM[i][j] != math.inf: #only continue if not inf, we want a smaller cost
                    num_states += 1
                    RCM_copy = np.array(copy.deepcopy(currentRCM))
                    modify_result = self.updateMatrix(RCM_copy, i, j, currentNode.bound, cities, currentNode.path)
                    if modify_result[1] == True:  # if it is a leaf node, update BSSF
                        newNode = modify_result[0]
                        city_index = newNode.current_city._index
                        if self._scenario._edge_exists[city_index][0]:
                            temp = TSPSolution(modify_result[0].path)
                            #if our temp path cost is less than the BSSF, we update BSSF to the lower cost path
                            if temp.cost < lowest_cost:
                                bssf = TSPSolution(modify_result[0].path)
                                lowest_cost = bssf.cost
                                num_updates += 1
                    else:  # if not leaf, push onto heap. Sorted by score.
                        heapq.heappush(heap, (modify_result[0].score, modify_result[0]))
                        max_heap_len = self.check_heap_len(heap, max_heap_len)

    # ending. Setting end values.
    end_time = time.time()
    results['cost'] = bssf.cost
    results['time'] = end_time - start_time
    results['count'] = num_updates
    results['soln'] = bssf
    results['max'] = max_heap_len
    results['total'] = num_states
    results['pruned'] = pruned
    return results
