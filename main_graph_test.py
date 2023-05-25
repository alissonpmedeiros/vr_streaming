from controllers import graph_controller
from controllers import bs_controller
from controllers import dijkstra_controller
from controllers import json_controller
from controllers import config_controller

from pprint import pprint as pprint

CONFIG = config_controller.ConfigController.get_config()

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']



base_station_set = json_controller.DecoderController.decode_net_config_file()

#pprint(base_station_set)
#a = input('')

#a = input('')
graph = graph_controller.GraphController.get_graph(base_station_set)

graph_controller.GraphController.print_graph(graph)


start_node = base_station_set['3']
target_node = base_station_set['7']
print(f'\n################ START NODE ################\n')
print(start_node.bs_name) 
#pprint(graph.graph)
#a = input('')
dijkstra_controller.DijkstraController.get_shortest_path_all_paths(graph, start_node, base_station_set)
dijkstra_controller.DijkstraController.get_E2E_shortest_path_all_paths(graph, start_node, base_station_set)
dijkstra_controller.DijkstraController.get_E2E_throughput_widest_path_all_paths(graph, start_node, base_station_set)
'''
'''
a = input('')

print(f'\n##################### THROUGHPUT ########################\n')

path, e2e_throughput = dijkstra_controller.DijkstraController.get_widest_path(
    graph, start_node, target_node
)

print(" -> ".join(path))
print(e2e_throughput)

print(f'\n##################### E2E LATENCY ########################\n')

path, e2e_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
    graph, start_node, target_node
)


print(" -> ".join(path))
print(e2e_latency)
net_latency = e2e_latency - (target_node.node_latency + start_node.wireless_latency)

result = {
    "e2e_latency": round(e2e_latency, 2),
    "network_latency": round(net_latency, 2),
    "destination_latency": round(target_node.node_latency, 2)
}


print(f'\n##################### NETWORK LATENCY ########################\n')

path, e2e_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
    graph, start_node, target_node
)


print(" -> ".join(path))
print(e2e_latency)

'''
a = input('ENTER TO PASS')

'''

