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
import time
import random
import logging
from random import choice
from timeit import default_timer as timer
from pprint import pprint as pprint

logging.basicConfig(level=logging.INFO)
'''
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
'''

MAX_THROUGHPUT = 250


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

CDN_SERVER_ID = 136
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

def full_resolutions(flow_set: dict) -> bool:
    result = True
    flow_in_max_throughput = 0
    
    for flow in flow_set.values():
        if flow['throughput'] < MAX_THROUGHPUT:
            result = False
        else:
            flow_in_max_throughput += 1
    
    logging.info(f'\nFLOWS IN MAX THROUGHPUT: {flow_in_max_throughput} OUT OF {len(flow_set)}\n')
    return result

def get_current_throughput(flow_set: dict):
    current_throughput = 0
    
    for flow in flow_set.values():
        current_throughput += flow['throughput']
        
    return current_throughput

def get_expected_throughput(flow_set: dict):
    expected_throughput = 0
    
    for flow in flow_set.values():
        expected_throughput += bitrate_profiles.get_next_throughput_profile(flow['throughput'])
    
    return expected_throughput

def flow_fairness_selection(flow_set):
    """ return a list of flows that will be not prioritized """
    flow_set_size = len(flow_set)
    floor = 10 # PERCENTAGE
    roof = 30 # PERCENTAGE
    
    percentage_deallocated_flows = random.randint(floor, roof) / 100
    total_deallocated_flows = int(flow_set_size * percentage_deallocated_flows)   
    deallocated_flows_list = random.sample(range(0, flow_set_size-1), total_deallocated_flows)
    
    return deallocated_flows_list

def get_available_bandwidth_of_node_edges(graph, src: str):
    available_bandwidth = 0
    src_node = graph.graph[src]
    
    for edge in src_node['edges']:
        edge_id = 'BS'+str(edge)
        available_bandwidth += graph.graph[src][edge_id]['available_bandwidth']
        
    return round(available_bandwidth, 2)
    


if __name__ == '__main__':
    ### BASE STATIONS ###
    logging.info(f'\n*** decoding base stations ***')
    base_station_set = json_controller.decode_net_config_file()  

    ### MECS ###
    mec_controller.MecController.create_mec_servers(
        base_station_set, OVERALL_MECS
    )

    logging.info(f'\n*** decoding mecs ***')
    mec_set = json_controller.decoding_to_dict(
        data_dir, mecs_file
    )
    
    logging.info(f'\n*** initializing mecs ***')
    bs_controller.BaseStationController.initialize_mec_nodes(base_station_set, mec_set)
    
    ### HMDS ###
    #logging.info(f'\n*** creating hmds ***')
    #hmd_controller.HmdController.create_hmds()

    logging.info(f'\n*** decoding hmds ***')
    hmds_set = json_controller.decoding_to_dict(
        data_dir, hmds_file
    )

    ### GRAPH ###
    logging.info(f'\n*** getting graph ***')
    graph = graph_controller.GraphController.get_graph(base_station_set)

    
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
    
    logging.info(f'\n*** creating video and client servers ***')
    

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
                        'throughput': bitrate_quotas[first_hmd_quota]['throughput'],
                        'previous_throughput': None
                }
                pairs += 1
                clients += 1
                video_clients.remove(client) 
        clients = 0   
        video_servers.remove(server)

    logging.info(f'\n*** initializing route_set ***')
    network_controller.NetworkController.initialize_route_set(hmds_set, route_set)

    cdn_graph_id = 'BS' + str(CDN_SERVER_ID)
    
    logging.info(f'\n*** starting system ***')
    
    while True:
        
        #start = timer()
        flows_order = []
        prioritized_served_flows = [] 
        non_prioritized_served_flows = []

        for i in range(len(flow_set)): 
            if i not in video_servers:
                flows_order.append(i) 
        
        random.shuffle(flows_order)
        
        #update_hmds_bandwidth_allocation(hmds_set, flow_set)
        
        current_throughput = get_current_throughput(flow_set)
        expected_throughput = get_expected_throughput(flow_set)
       
        deallocated_flows_list = []
        
        if ITERATION > 1:
            deallocated_flows_list = flow_fairness_selection(flows_order)  
            
        
        logging.info(f'\n\n################ ITERATION ################\n')
        logging.info(f'ITERATION: {ITERATION}')
        logging.info(f'updating hmd positions...')
        hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
        #network_controller.NetworkController.print_network(base_station_set, hmds_set)
        
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***decallocating route of non-prioritized flows...')
            logging.info(f'{len(deallocated_flows_list)}/{len(flow_set)} flows will be deallocated')
            for flow_id in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                flow_throughput = flow_set[flow_id]['throughput']
                flow_set[flow_id]['previous_throughput'] = flow_throughput
                flow = flow_set[flow_id]
                src_id = flow['client']
                route_id = str(src_id)
                route = route_set[route_id]['route']
                logging.debug(f'\n dealocating {flow_throughput} Mbps from the following route:')
                logging.debug('->'.join(route))
                
                network_controller.NetworkController.deallocate_bandwidth(graph, route_set, flow_set, route_id, flow_id)
                
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***new CDN edge throughput: {cdn_bandwidth}') 

        
        logging.info(f'\n****************************************************')
        logging.info(f'\n***allocating bandwidth for prioritized flows...')
        
        for flow_id in flows_order:
            if flow_id not in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                route_id = str(src_id)
                
                flow_throughput = flow['throughput']
                
                previous_throughput = flow_throughput
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
               
                logging.debug(f'\n___________________________________________')
                logging.debug(f'*** \nFLOW ID: {flow_id} *** ') 
                logging.debug(f'\n*** REQUESTING {required_throughput} Mbps ***\n')
                        
                video_client = hmds_set[str(src_id)]
                source_node_id = str(hmds_set[str(src_id)].current_base_station)
                previous_source_node_id = str(hmds_set[str(src_id)].previous_base_station)
                
                previous_source_node = None
                if previous_source_node_id:
                    previous_source_node = base_station_set[previous_source_node_id]
                
                source_node = base_station_set[source_node_id]

                mec_server = mec_set[str(dst_id)]
                video_server = mec_server.video_server
                video_id = list(video_server.video_set.keys())[0]
                
                manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                already_deallocated = False
                prioritized_flow = True
            
                required_throughput = network_controller.NetworkController.allocate_bandwidth(
                    graph, route_set, route_id, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id, required_throughput, already_deallocated, prioritized_flow
                )
               
                logging.debug(f'\nswitching resolution...\n')
                
                hmd_controller.HmdController.switch_resolution_based_on_throughput(
                    video_client, manifest, required_throughput
                )
                
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                logging.debug(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                
                prioritized_served_flows.append(flow_id)
            
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***reallocating bandwidth for non-prioritized flows...')
            #a = input('')
            flow_count = 0
            for flow_id in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                flow_count += 1
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                route_id = str(src_id)
                
                flow_throughput = flow['previous_throughput']
                
                previous_throughput = flow_throughput
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
                
                
                logging.debug(f'\n___________________________________________')
                logging.debug(f'*** \nFLOW ID: {flow_id} - NON-PRIORITIZED ({flow_count}/{len(deallocated_flows_list)})*** ') 
                logging.debug(f'\n*** REQUESTING {required_throughput} Mbps ***')
                logging.debug(f'*** PREVIOUS THROUGHPUT: {previous_throughput} Mbps ***\n')
                            
                video_client = hmds_set[str(src_id)]
                source_node_id = str(hmds_set[str(src_id)].current_base_station)
                source_node = base_station_set[source_node_id]
           
                mec_server = mec_set[str(dst_id)]
                video_server = mec_server.video_server
                video_id = list(video_server.video_set.keys())[0]
                
                manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                already_deallocated = True
                prioritized_flow = False
            
                required_throughput = network_controller.NetworkController.allocate_bandwidth(
                    graph, route_set, route_id, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id, required_throughput, already_deallocated, prioritized_flow
                )
                
                
                cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                logging.debug(f'\n***new CDN edge throughput: {cdn_bandwidth}') 
                
                logging.debug(f'\nswitching resolution...\n')
                
                hmd_controller.HmdController.switch_resolution_based_on_throughput(
                    video_client, manifest, required_throughput
                )
                
                logging.debug(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                
                non_prioritized_served_flows.append(flow_id)
                    
                #a = input('type to process the next flow...')
        
        #end = timer()
        #print(f'\nelapsed time: {end - start}')
        updated_throughput = get_current_throughput(flow_set)
        logging.info(f'\n****************************************************\n')
        logging.info(f'\nPREVIOUS THROUGHPUT: {current_throughput} Mbps')
        logging.info(f'EXPECTED THROUGHPUT: {expected_throughput} Mbps')
        logging.info(f'UPDATED  THROUGHPUT: {updated_throughput} Mbps')
        cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
        logging.info(f'\n***current CND edge throughput: {cdn_bandwidth}') 
        
        full_resolutions(flow_set)
        #generate_networks.plot_graph(graph.graph)
        
        print(f'\n*** checking all bandwidths synchonization ***')
        for flow_id in flows_order:
            #print(f'checking flow {flow_id}')
            network_controller.NetworkController.check_bandwidth_synchonization(graph, flow_set, route_set, flow_id)
        print(f'\n*** finish checking all bandwidths synchonization ***')
        
        time.sleep(1)
        
        '''
        if ITERATION == 3:
            print(f'\nDEALOCATING ALL BW\n')
            for flow_id in flows_order:
                flow = flow_set[flow_id]
                src_id = flow['client']
                dst_id = flow['server']
                route_id = str(src_id)
                flow_throughput = flow['throughput'] 
                network_controller.NetworkController.deallocate_bandwidth(graph, route_set, flow_set, route_id, flow_id)
           
            pprint(graph.graph) 
            a = input('type to continue...')
        
        '''
        ITERATION += 1
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



