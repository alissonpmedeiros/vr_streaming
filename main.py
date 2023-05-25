""" controller modules """
from controllers import config_controller
from controllers import hmd_controller 
from controllers import json_controller
from controllers import mec_controller
from controllers import graph_controller
from controllers import dijkstra_controller
from utils.network import generate_networks 
from controllers import network_controller
from matplotlib import pyplot as plt
from models.bitrates import BitRateProfiles
bitrate_profiles = BitRateProfiles()
import time

'''import typing 
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.migration_ABC import Migration

from models.migration_algorithms.la import LA
from models.migration_algorithms.lra import LRA
from models.migration_algorithms.scg import SCG
from models.migration_algorithms.dscp import DSCP
from models.migration_algorithms.nm import NoMigration
from models.migration_algorithms.am import AlwaysMigrate'''

"""others modules"""
import sys
import random
from random import choice
from pprint import pprint as pprint

OVERALL_MECS = 50
OVERALL_VIDEO_SERVERS = 5
OVERALL_VIDEO_CLIENTS = 20
CLIENTS_PER_SERVER = 4


### CONFIG ###

CONFIG = config_controller.ConfigController.get_config()

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']

#hmd_controller = hmd_controller.HmdController()
json_controller = json_controller.DecoderController()
network_controller = network_controller.NetworkController()
dijkstra_controller = dijkstra_controller.DijkstraController()

### FUNCTIONS ###

'''def check_algorithm():
    if sys.argv[1] == 'no':
        return NoMigration()
    elif sys.argv[1] == 'scg':
        return SCG()
    elif sys.argv[1] == 'am':
        return AlwaysMigrate()
    elif sys.argv[1] == 'la':
        return LA()
    elif sys.argv[1] == 'lra':
        return LRA()
    elif sys.argv[1] == 'dscp':
        return DSCP()
    else:
        print('*** algorithm not found! ***')
        a = input('')
        

def check_service_migration(migration_algorithm: 'Migration'):
    print('\n*** CHECKING MIGRATION ***')
    
    migration_algorithm.check_services(
        base_station_set,
        mec_set, 
        hmds_set,
        graph,
    ) 
 '''       

def start_system():
    plt.figure(figsize=(12, 12))

    while True:
        network_controller.generate_network_plot(base_station_set, hmds_set)
        hmd_controller.update_hmd_positions(base_station_set, hmds_set)
        a = input('')
        
        '''
        INITIAL SETUP
        1. define the connections between hmds and video servers
        2. update hmds positions
        3. switch the video resolution of the hmds based on initial quotas 
        4. allocate bandwidth for each connection
        
        
        AFTER STARTING THE SYSTEM
        1. update hmds positions
        2. check throughput of each connection
        3. update banwidth allocation
        4. calculate the bitrate of all hmds
        5. switch the resoluitons of the videos

        '''



### BASE STATIONS ###

base_station_set = json_controller.decode_net_config_file()

### MECS ###
mec_controller.MecController.create_mec_servers(
    base_station_set, OVERALL_MECS
)

mec_set = json_controller.decoding_to_dict(
    data_dir, mecs_file
)
 
### HMDS ###
hmd_controller.HmdController.create_hmds()

hmds_set = json_controller.decoding_to_dict(
    data_dir, hmds_file
)

### ROUTES###
route_set = {}

### GRAPH TEST###

graph = graph_controller.GraphController.get_graph(base_station_set)

### VIDEO SERVERS AND CLIENTS ###


video_servers = []
for _ in range(OVERALL_VIDEO_SERVERS):
    video_servers.append(random.randint(0, OVERALL_MECS-1))
    
video_clients = []
for _ in range(OVERALL_VIDEO_CLIENTS):
    video_clients.append(choice([i for i in range(0,OVERALL_MECS-1) if i not in video_servers]))

connections = {}

clients = 0
pairs = 0

#print(len(video_servers))
#print(video_servers)
#print(len(video_clients))
#print(video_clients)

for server in video_servers.copy():
    for client in video_clients.copy():
        print(f'pair: {client} -> {server}')
        if clients == CLIENTS_PER_SERVER-1:
            break
        else:
            connections[pairs] = {
                    'server': server,
                    'client': client,
            }
            pairs += 1
            clients += 1
            video_clients.remove(client) 
    clients = 0   
    video_servers.remove(server)

    

#pprint(connections)
#a = input('')
    
        

###########################################################################

### THROUGHPUT TEST###

first_hmd_id = list(hmds_set.keys())[0]
first_hmd = hmds_set[first_hmd_id]


first_mec_id = list(mec_set.keys())[0]
first_mec = mec_set[first_mec_id]

first_server = first_mec.video_server

first_video_id = list(first_server.video_set.keys())[0]

src_node_id = 49
dst_node_id = 3

manifest = hmd_controller.HmdController.request_manifest(mec_set, first_video_id)     

bitrate_quotas = bitrate_profiles.get_bitrate_quota_profiles()
first_hmd_quota = first_hmd.services_set[0].quota.name
first_hmd.video_client.current_throughput = bitrate_quotas[first_hmd_quota]['throughput']

source_node = base_station_set[str(src_node_id)]
target_node = base_station_set[str(dst_node_id)]

required_throughput = first_hmd.video_client.current_throughput

while True:
    #print(f'\n##################### THROUGHPUT ########################\n')
    print(f'\n################ ITERATION ################\n')
    #pprint(first_hmd.video_client)
    
    print(f'updating hmd positions...')
    hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
    
    
    
    #a = input('')
    #required_throughput = random.randint(40, 50)
    #total_throughput += required_throughput
    
    #print(f'total throughput: {total_throughput} Mbps')
    print(f'required throughput: {required_throughput} Mbps')
     
    print(f'requesting banwidth allocation...')
    required_throughput = network_controller.allocate_bandwidth(
        graph, route_set, source_node, target_node, required_throughput
    )
    
    print(f'\nswitching resolution...')
    hmd_controller.HmdController.switch_resolution_based_on_throughput(first_hmd, manifest, required_throughput)
    
    previous_throughput = required_throughput
    required_throughput = bitrate_profiles.get_next_throughput_profile(required_throughput)
    print(f'trying to upgrade video resolution from {previous_throughput} -> {required_throughput}...')
    
    a = input('\npress enter to continue!\n')
    generate_networks.plot_graph(graph.graph)
    time.sleep(0.5)
    
    '''
    network_controller.allocate_bandwidth(
        graph, route_set, src, dst, required_throughput
    )
    time.sleep(0.5)
    
    generate_networks.plot_graph(graph.graph)
    #a = input('\npress enter to continue!\n')
    
    
    option = input(f'\ntype 1 to delete route from {source_node.bs_name} -> {target_node.bs_name}: ')
    if option == '1':
        
        network_controller.deallocate_bandwidth(
            graph, route_set, source_node.bs_name
        )
        
        generate_networks.plot_graph(graph.graph)
    '''
        
    #if cont % 10000 == 0:
    #    generate_networks.plot_graph(graph.graph)
    #cont += 1
    #break


###########################################################################

### HMD TEST ###

'''
'''
first_hmd_id = list(hmds_set.keys())[0]
first_hmd = hmds_set[first_hmd_id]


first_mec_id = list(mec_set.keys())[0]
first_mec = mec_set[first_mec_id]

first_server = first_mec.video_server

first_video_id = list(first_server.video_set.keys())[0]


### RESOLUTION TEST ###
#print(f'\n*** Starting video operations ***\n')
#print(f'requesting manifest of video id: {first_video_id}')
manifest = hmd_controller.request_manifest(mec_set, first_video_id)

#pprint(manifest)


### PLOT TEST ###

start_system()





###########################################################################

### SHORTEST AND WIDEST PATH TEST###

print(f'\n################ START NODE ################\n')
print(source_node.bs_name) 
#pprint(graph.graph)
#a = input('')
dijkstra_controller.get_shortest_path_all_paths(
    graph, source_node, base_station_set
)

dijkstra_controller.get_E2E_shortest_path_all_paths(
    graph, source_node, base_station_set
)

dijkstra_controller.get_E2E_throughput_widest_path_all_paths(
    graph, source_node, base_station_set
)


print(f'\n##################### THROUGHPUT ########################\n')

path, e2e_throughput = dijkstra_controller.get_widest_path(
    graph, source_node, target_node
)

print(" -> ".join(path))
print(e2e_throughput)

print(f'\n##################### E2E LATENCY ########################\n')

path, e2e_latency = dijkstra_controller.get_ETE_shortest_path(
    graph, source_node, target_node
)

print(" -> ".join(path))
print(e2e_latency)
net_latency = e2e_latency - (target_node.node_latency + source_node.wireless_latency)

result = {
    "e2e_latency": round(e2e_latency, 2),
    "network_latency": round(net_latency, 2),
    "destination_latency": round(target_node.node_latency, 2)
}


print(f'\n##################### NETWORK LATENCY ########################\n')

path, e2e_latency = dijkstra_controller.get_shortest_path(
    graph, source_node, target_node
)


print(" -> ".join(path))
print(e2e_latency)




al = input('enter to continue')



###########################################################################






