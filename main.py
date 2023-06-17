""" controller modules """
from controllers import config_controller
from controllers import bs_controller
from controllers import hmd_controller 
from controllers import json_controller
from controllers import mec_controller
from controllers import graph_controller
from controllers import dijkstra_controller
from utils.network import generate_networks 
from controllers import network_controller
from models.bitrates import BitRateProfiles
bitrate_profiles = BitRateProfiles()



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
import time
from timeit import default_timer as timer
import random
from random import choice
from pprint import pprint as pprint
import multiprocessing
from threading import Thread
import pickle


MAX_THROUGHPUT = 250
LOGS = True

### CONFIG ###

CONFIG = config_controller.ConfigController.get_config()

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']


OVERALL_MECS = CONFIG['MEC_SERVERS']['OVERALL_MECS']
OVERALL_VIDEO_SERVERS = 1
OVERALL_VIDEO_CLIENTS = CONFIG['NETWORK']['HMDS']
#OVERALL_VIDEO_CLIENTS = 5
CLIENTS_PER_SERVER = OVERALL_VIDEO_CLIENTS / OVERALL_VIDEO_SERVERS

CDN_SERVER_ID = 226
CDN_CLIENT_ID = 161


ITERATION = 1

#hmd_controller = hmd_controller.HmdController()
json_controller = json_controller.DecoderController()

dijkstra_controller = dijkstra_controller.DijkstraController()


def start_system():

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

def full_resolutions() -> bool:
    for flow in flow_set.values():
        if flow['throughput'] < MAX_THROUGHPUT:
            return False
    return True 



if __name__ == '__main__':
    #MULTIPROCESSING MANAGERS 
    #manager = multiprocessing.Manager()

    
    ### BASE STATIONS ###
    print(f'\n*** decoding base stations ***')
    base_station_set = json_controller.decode_net_config_file()  

    ### MECS ###
    mec_controller.MecController.create_mec_servers(
        base_station_set, OVERALL_MECS
    )

    print(f'\n*** decoding mecs ***')
    mec_set = json_controller.decoding_to_dict(
        data_dir, mecs_file
    )
    
    print(f'\n*** initializing mecs ***')
    bs_controller.BaseStationController.initialize_mec_nodes(base_station_set, mec_set)
    
    ### HMDS ###
    #print(f'\n*** creating hmds ***')
    #hmd_controller.HmdController.create_hmds()

    print(f'\n*** decoding hmds ***')
    hmds_set = json_controller.decoding_to_dict(
        data_dir, hmds_file
    )

    ### GRAPH ###
    print(f'\n*** getting graph ***')
    graph = graph_controller.GraphController.get_graph(base_station_set)
    #graph = manager.dict()
    #graph.update(graph_copy.graph)
    
    
    ### ROUTES###
    route_set = {}

    ### VIDEO SERVERS AND CLIENTS ###
    video_servers = []
    #for _ in range(OVERALL_VIDEO_SERVERS):
    #    video_servers.append(random.randint(0, OVERALL_MECS-1))
    video_servers.append(CDN_SERVER_ID)
        
    video_clients = []

    for _ in range(OVERALL_VIDEO_CLIENTS):
        #video_clients.append(choice([i for i in range(0,OVERALL_VIDEO_CLIENTS+1) if i not in video_servers and i not in video_clients]))
        video_clients.append(choice([i for i in range(0,OVERALL_VIDEO_CLIENTS)]))

    #print(f'video servers: {video_servers}')
    #print(f'overall mecs : {OVERALL_MECS} -> {video_servers}')
    #print(f'overall video clients: {OVERALL_VIDEO_CLIENTS} -> {video_clients}')
    flow_set = {}

    clients = 0
    pairs = 0

    process_list = []
    
    print(f'\n*** creating video and client servers ***')
    

    for server in video_servers.copy():
        for client in video_clients.copy():
            if clients == CLIENTS_PER_SERVER:
                break
            else:
                mec_id = str(server)
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

    
    print(f'\n*** starting system ***')
    
    while True:
        
        start = timer()
        flows_order = []
        served_flows = []

        for i in range(len(flow_set)): 
            if i not in video_servers:
                flows_order.append(i) 
        
        random.shuffle(flows_order)
        
        print(f'\n################ ITERATION ################\n')
        print(f'ITERATION: {ITERATION}')
        ITERATION += 1
        if LOGS:
            print(f'updating hmd positions...')
        hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
        #network_controller.NetworkController.print_network(base_station_set, hmds_set)
        #pprint(graph.graph)
        
        for flow_id in flows_order:
            
            
            flow = flow_set[flow_id]
            
            src_id = flow['client']
            dst_id = flow['server']
            
            flow_throughput = flow['throughput']
            
            previous_throughput = flow_throughput
            required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
            
            if previous_throughput == MAX_THROUGHPUT:
                if LOGS:
                    print(f'\nmaximum throughput reached!\n')
                    
            else:
                if LOGS:
                    print(f'\n___________________________________________')
                    #print(f'\nFLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                    #print(f'\nupgrading video resolution from {previous_throughput} -> {required_throughput}...')
                    print(f'*** \nFLOW ID: {flow_id} *** \n') 
                        
                video_client = hmds_set[str(src_id)]
                source_node_id = str(hmds_set[str(src_id)].current_base_station)
                #TODO: to be undone
                source_node = base_station_set[source_node_id]
                #source_node = base_station_set[str(CDN_CLIENT_ID)]

                mec_server = mec_set[str(dst_id)]
                video_server = mec_server.video_server
                video_id = list(video_server.video_set.keys())[0]
                
                manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
            
                required_throughput = network_controller.NetworkController.allocate_bandwidth(
                    graph, hmds_set, route_set, source_node, target_node, flow_set, served_flows, flow_id, required_throughput
                )
                
                if LOGS:
                    print(f'\nswitching resolution...\n')
                
                hmd_controller.HmdController.switch_resolution_based_on_throughput(
                    video_client, manifest, required_throughput
                )
                #flow['throughput'] = required_throughput
                flow_set[flow_id]['throughput'] = required_throughput
                
                served_flows.append(flow_id)
                
                if LOGS:
                    print(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                   
                    
                #a = input('')

                
                
            
        
        
        
        end = timer()
        #pprint(flow_set)
        print(f'\nelapsed time: {end - start}')
        
        #pprint(flow_set)
        
        '''
        if ITERATION % 1 == 0:
            print(f'printing graph...')    
            generate_networks.plot_graph(graph.graph)
        
        if full_resolutions():
            print(f'printing graph...')    
            generate_networks.plot_graph(graph.graph)
            a = input('FINISHED!')
        '''
            
        
        #time.sleep(3)
    

    '''

    ###########################################################################

    ### HMD TEST ###

    '''
    '''
    first_hmd_id = list(hmds_set.keys())[0]
    hmd = hmds_set[first_hmd_id]


    mec_id = list(mec_set.keys())[0]
    mec_server = mec_set[mec_id]

    video_server = mec_server.video_server

    video_id = list(video_server.video_set.keys())[0]


    ### RESOLUTION TEST ###
    #print(f'\n*** Starting video operations ***\n')
    #print(f'requesting manifest of video id: {first_video_id}')
    manifest = hmd_controller.request_manifest(mec_set, video_id)

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


    '''



