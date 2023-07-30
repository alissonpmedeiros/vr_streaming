from controllers import graph_controller
from controllers import bs_controller
from controllers import path_controller
from pprint import pprint as pprint
import sys
import heapq

#base_station_set = bs_controller.BaseStationController.load_base_stations()


#custom_graph = graph_controller.GraphController.get_graph(base_station_set)

#start_node = base_station_set['3']
#target_node = base_station_set['7']

############################################################

'''
path, e2e_latency = dijkstra_controller.DijkstraController.get_ETE_latency(
    graph, start_node, target_node
)

print(f'\n##################### LATENCY ########################\n')

print(" -> ".join(path))
print(e2e_latency)
net_latency = e2e_latency - (target_node.node_latency + start_node.wireless_latency)

result = {
    "e2e_latency": round(e2e_latency, 2),
    "network_latency": round(net_latency, 2),
    "destination_latency": round(target_node.node_latency, 2)
}
a = input('ENTER TO PASS')

'''
# pprint(result, width=1) 
print(f'\n##################### THROUGHPUT ########################\n')

def printpath(parent, vertex, target):
    # global parent 
    if (vertex == 0):
        return
    printpath(parent, parent[vertex], target)
    print(vertex ,end="\n" if (vertex == target) else " -> ")
 
# Function to return the maximum weight
# in the widest path of the given graph
def widest_path_problem(Graph, src, target):
     
    # To keep track of widest distance
    widest = [-10**9]*(len(Graph))
    print(f'WIDEST: {widest}')
 
    # To get the path at the end of the algorithm
    parent = [0]*len(Graph)
    print(f'PARENT: {parent}')
 
    # Use of Minimum Priority Queue to keep track minimum
    # widest distance vertex so far in the algorithm
    container = []
    container.append((0, src))
    widest[src] = 10**9
    print(f'WIDEST: [{src}]: {widest[src]}')
    
    container = sorted(container)
    print(f'CONTAINER: {container}')
    
    print(f'\nSTARTING WHILE LOOP')
    while (len(container)>0):
        print(f'\n#############################################\n')
        temp = container[-1]
        #print(f'TEMP RECEIVES CONTAINER LAST POSITION: {temp}')
        current_src = temp[1]
        print(f'CURRENT VERTEX: {current_src}')
        #print(f'DELETE CONTAINER LAST POSITION[-1], WHICH HAS: {container[-1]}')
        del container[-1]
        print(f'CONTAINER: {container}')
        
        for vertex in Graph[current_src]:
            
            #print(f'\nCURRENT VERTEX VALUE: WEIGHT -> {vertex[0]} | DESTINATION -> {vertex[1]}')
            
            print(f'\n***CURRENT VERTEX({current_src}) -> DESTINATION({vertex[1]}): WEIGHT {vertex[0]}')
 
            # Finding the widest distance to the vertex
            # using current_source vertex's widest distance
            # and its widest distance so far
            
            print(f'VERTEX {current_src} DIST -> {widest[current_src]}')
            
            print(f'DESTINATION {vertex[1]} DIST -> {widest[vertex[1]]}')
            
            print(f'DISTANCE = MAX(DESTINATION {vertex[1]} DIST | MIN (VERTEX {current_src} DIST | VERTEX {current_src} DIST))')
            
            print(f'DISTANCE = MAX({widest[vertex[1]]} | MIN ({widest[current_src]} | {vertex[0]}))')
            
            distance = max(widest[vertex[1]],
                           min(widest[current_src], vertex[0])
                        )
            
            print(f'DISTANCE: {distance}')
            
            # Relaxation of edge and adding into Priority Queue
            if (distance > widest[vertex[1]]):
                #print(f'\n____________________________________________________')
                #print(f'PASSED: if (distance > widest[vertex[1]]):')
                # Updating bottle-neck distance
                widest[vertex[1]] = distance
                #print(f'widest[vertex[1]] = distance -> widest[{vertex[1]}] = {distance}')
                
                # To keep track of parent
                parent[vertex[1]] = current_src
                #print(f'parent[vertex[1]] = current_src -> parent[{vertex[1]}] = {current_src}')
    
                # Adding the relaxed edge in the priority queue
                container.append((distance, vertex[1]))
                #print(f'APPENDING [{distance, vertex[1]}] TO CONTAINER')
                
                container = sorted(container)
                #print(f'SORTED CONTAINER: {container}')
                #print(f'____________________________________________________')
            a = input('\nEnter to Continue...\n')
    
    print(f'\n\nRESULTS\n')
    printpath(parent, target, target)
    return widest[target]
        

# Graph representation
graph = [[] for i in range(5)] #TODO: graph should have one extra position 
no_vertices = 4
# Adding edges to graph

# Resulting graph
#1--2
#|  |
#4--3

# Note that order in pair is (distance, vertex)
graph[1].append((1, 2))
graph[1].append((2, 4))
#graph[4].append((2, 1))#
#graph[2].append((1, 1))#
graph[4].append((5, 3))
graph[2].append((3, 3))
#graph[3].append((3, 2))#
#graph[3].append((5, 4))#
'''
'''
'''
for bs_id, base_station in base_station_set.items():
    for edge in base_station.edges:
        int_edge = int(edge)
        edge_index = base_station.edges.index(edge)
        graph[base_station.id].append((base_station.edge_net_throughputs[edge_index], int_edge))
    
'''
#print(f'\n\nRESULTS')
print(widest_path_problem(graph, 1, 3))
#widest_path_problem(graph, 1, 3)