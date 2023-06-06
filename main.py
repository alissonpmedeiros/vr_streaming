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

OVERALL_MECS = 1
OVERALL_VIDEO_SERVERS = 1
OVERALL_VIDEO_CLIENTS = 7
CLIENTS_PER_SERVER = OVERALL_VIDEO_CLIENTS / OVERALL_VIDEO_SERVERS

MAX_THROUGHPUT = 250


### CONFIG ###

CONFIG = config_controller.ConfigController.get_config()

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']

#hmd_controller = hmd_controller.HmdController()
json_controller = json_controller.DecoderController()

dijkstra_controller = dijkstra_controller.DijkstraController()


def start_system():
    plt.figure(figsize=(12, 12))

    while True:
        network_controller.NetworkController.generate_network_plot(base_station_set, hmds_set)
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
#for _ in range(OVERALL_VIDEO_SERVERS):
#    video_servers.append(random.randint(0, OVERALL_MECS-1))
video_servers.append(2)
    
video_clients = []

for _ in range(OVERALL_VIDEO_CLIENTS):
    video_clients.append(choice([i for i in range(0,OVERALL_VIDEO_CLIENTS+1) if i not in video_servers and i not in video_clients]))

#print(f'video servers: {video_servers}')
#print(f'overall mecs : {OVERALL_MECS} -> {video_servers}')
#print(f'overall video clients: {OVERALL_VIDEO_CLIENTS} -> {video_clients}')
flow_set = {}

clients = 0
pairs = 0


def full_resolutions(flow_set: dict) -> bool:
    for flow in flow_set.values():
        if flow['throughput'] < MAX_THROUGHPUT:
            return False
    return True 

for server in video_servers.copy():
    for client in video_clients.copy():
        if clients == CLIENTS_PER_SERVER:
            break
        else:
            hmd = hmds_set[str(client)]

            mec_id = server
            mec_server = mec_set[str(mec_id)]

            first_server = mec_server.video_server

            first_video_id = list(first_server.video_set.keys())[0]
            manifest = hmd_controller.HmdController.request_manifest(mec_set, first_video_id) 
            bitrate_quotas = bitrate_profiles.get_bitrate_quota_profiles()
            first_hmd_quota = hmds_set[str(client)].services_set[0].quota.name
            flow_set[pairs] = {
                    'server': server,
                    'client': client,
                    'throughput': bitrate_quotas[first_hmd_quota]['throughput']
            }
            pairs += 1
            clients += 1
            video_clients.remove(client) 
    clients = 0   
    video_servers.remove(server)

    

#pprint(flow_set)
#a = input('')
    
        

###########################################################################

### THROUGHPUT TEST###


while True:
    
    flows_order = []
    served_flows = []

    for i in range(len(flow_set)): 
        if i not in video_servers:
            flows_order.append(i) 
    
    random.shuffle(flows_order)
    
    print(f'\n################ ITERATION ################\n')
    
    print(f'updating hmd positions...')
    hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
    #network_controller.NetworkController.print_network(base_station_set, hmds_set)
    
    for flow_id in flows_order:
        flow = flow_set[flow_id]
        src_id = flow['client']
        dst_id = flow['server']
        
        flow_throughput = flow['throughput']
        
        previous_throughput = flow_throughput
        required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
        
        if previous_throughput == MAX_THROUGHPUT:
            print(f'\nmaximum throughput reached!\n')
                
        else:
            print(f'\n___________________________________________')
            print(f'\nupgrading video resolution from {previous_throughput} -> {required_throughput}...')
        
            #source_node = hmds_set[str(src_id)].current_base_station
            #target_node = hmds_set[str(dst_id)].current_base_station
            source_node = base_station_set[str(src_id)]
            
          
            target_node = base_station_set[str(dst_id)]
            
            
            print(f'\nrequesting {required_throughput} Mbps from {src_id} -> {dst_id}')
            required_throughput = network_controller.NetworkController.allocate_bandwidth(
                graph, route_set, source_node, target_node, required_throughput, flow_set, served_flows
            )
            print(f'\nswitching resolution...\n')
            hmd_controller.HmdController.switch_resolution_based_on_throughput(
                hmd, manifest, required_throughput
            )
            flow['throughput'] = required_throughput
          
            
        served_flows.append(flow_id)
        #print(f'\nserved flows: {served_flows}')
        #print(f'flow {flow_id} from {src_id} -> {dst_id}...')
        pprint(route_set)
        #a = input('')
    
    #route_set = {}
    #generate_networks.plot_graph(graph.graph)
    #a = input('type to continue..')
    
    #pprint(connections)
    #a = input('\ntype 1 to show graph!\n')
    #if full_resolutions(flow_set):
    #    generate_networks.plot_graph(graph.graph)
    #    a = input('type to continue..')
    #if a == '1':
    #    generate_networks.plot_graph(graph.graph)
    #time.sleep(0.5)
        
   


###########################################################################

### HMD TEST ###

'''
'''
first_hmd_id = list(hmds_set.keys())[0]
hmd = hmds_set[first_hmd_id]


mec_id = list(mec_set.keys())[0]
mec_server = mec_set[mec_id]

first_server = mec_server.video_server

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






