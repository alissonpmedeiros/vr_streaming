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



import typing
from typing import Dict
if typing.TYPE_CHECKING:
    from models.mec import Mec
    from models.graph import Graph 
    from models.base_station import BaseStation
    from models.quotas import Quota
    from models.migration_ABC import Migration
    from models.hmd import VrHMD

from models.migration_algorithms.lra import LRA
'''
from models.migration_algorithms.la import LA
from models.migration_algorithms.scg import SCG
from models.migration_algorithms.dscp import DSCP
from models.migration_algorithms.nm import NoMigration
from models.migration_algorithms.am import AlwaysMigrate
'''

"""others modules"""
import sys
import time
import random
import logging
from random import choice
from timeit import default_timer as timer
from pprint import pprint as pprint
from utils.csv_encoder import CSV

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

MIGRATION_ALGORITHM = LRA()

MAX_THROUGHPUT = 250


### CONFIG ###

CONFIG = config_controller.ConfigController.get_config()
json_controller = json_controller.DecoderController()

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']
results_dir = CONFIG['SYSTEM']['RESULTS_DIR']

ITERATION = 1

OVERALL_MECS = CONFIG['MEC_SERVERS']['OVERALL_MECS']
OVERALL_VIDEO_SERVERS = 1
OVERALL_VIDEO_CLIENTS = CONFIG['NETWORK']['HMDS']
#OVERALL_VIDEO_CLIENTS = 5
CLIENTS_PER_SERVER = OVERALL_VIDEO_CLIENTS / OVERALL_VIDEO_SERVERS

CDN_SERVER_ID = 136
CDN_CLIENT_ID = 161

'''
net_file_dir = CONFIG['NETWORK']['NETWORK_FILE_DIR']

network_controller.NetworkController.reduce_edge_net_latencies(net_file_dir, 'network.json')
a = input('')
'''

#FILE_NAME = 'bandwidth.csv'
ARG = sys.argv[1]
FILE_NAME = '{}.csv'.format(ARG)

FILE_HEADER = [
    'net_congested_level',
    'total_allocate_bw',
    'expected_allocated_bw',
    'updated_allocated_bw',
    'allocated_bw',
    'net_latency', 
    'desired_net_latency',
    'e2e_latency', 
    'average_fps',
    'standard_fps',
    'standard_8k', 
    'standard_4k', 
    'standard_2k', 
    'standard_1k',
    'high_fps',
    'high_8k',
    'high_4k',
    'high_2k',
    'high_1k',
    'full_8k'
]

CSV.create_file(results_dir, FILE_NAME, FILE_HEADER)

def calculate_network_overload(graph):
    
    graph_allocated_bw = 0
    graph_total_bw = 0

    visited_nodes = []
    for node, node_data in graph.items():
        for neighbor, neighbor_data in node_data.items():
            if neighbor.startswith('BS') and neighbor not in visited_nodes:
                allocated_bw = neighbor_data['allocated_bandwidth']
                total_bandwidth = neighbor_data['total_bandwidth']
                graph_allocated_bw += allocated_bw
                graph_total_bw += total_bandwidth
        visited_nodes.append(node)

    
    network_overload_percentage = (graph_allocated_bw * 100) / graph_total_bw 
    return round(network_overload_percentage, 2)

def get_fps_resolution(flow_set: dict):
    average_fps = 0
    standard_fps = 0
    standard_8k = 0 
    standard_4k = 0 
    standard_2k = 0 
    standard_1k = 0
    high_fps = 0
    high_8k = 0
    high_4k = 0
    high_2k = 0
    high_1k = 0
    full_8k = 0
    
    throughput_profiles = bitrate_profiles.get_throughput_profiles()
    
    for flow in flow_set.values():
        flow_throughput = flow['throughput']
        #  	Video Bitrate for 1K (1080p), Standard Frame Rate (24, 25, 30)
        if flow_throughput >= 10 and flow_throughput < 16:
            standard_1k += 1
            standard_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate'] 
            
        
        # Video Bitrate for 1K (1080p), High Frame Rate (48, 50, 60)
        elif flow_throughput >= 16 and flow_throughput < 20:
            high_1k += 1
            high_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
        
        #  	Video Bitrate for 2K (1440p), Standard Frame Rate (24, 25, 30)
        elif flow_throughput >= 20 and flow_throughput < 30:
            standard_2k += 1
            standard_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
        
        # Video Bitrate for 2K (1440p), High Frame Rate (48, 50, 60)
        elif flow_throughput >= 30 and flow_throughput < 44:
            high_2k += 1
            high_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
                
        #  	Video Bitrate for 4K, Standard Frame Rate (24, 25, 30)
        elif flow_throughput >= 44 and flow_throughput < 66:
            standard_4k += 1
            standard_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
            
        # Video Bitrate for 4K, High Frame Rate (48, 50, 60)
        elif flow_throughput >= 66 and flow_throughput < 100:
            high_4k += 1
            high_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
            
        #  	Video Bitrate for 8K, Standard Frame Rate (24, 25, 30)
        elif flow_throughput >= 100 and flow_throughput < 151:
            standard_8k += 1
            standard_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
            
        # Video Bitrate for 8K, High Frame Rate (48, 50, 60)
        elif flow_throughput >= 151 and flow_throughput < 300:
            high_8k += 1
            high_fps += throughput_profiles[flow_throughput]['frame_rate']
            average_fps += throughput_profiles[flow_throughput]['frame_rate']
            if flow_throughput >= MAX_THROUGHPUT:
                full_8k += 1
    
    total_standard_fps = standard_8k + standard_4k + standard_2k + standard_1k
    total_high_fps = high_8k + high_4k + high_2k + high_1k
    total_fps_flows = total_standard_fps + total_high_fps 
    
    average_fps = round(average_fps / total_fps_flows, 2) 
    standard_fps = round(standard_fps / total_standard_fps, 2)
    high_fps = round(high_fps / total_high_fps, 2)
    
    result = {
        'standard_fps': standard_fps,
        'standard_8k': standard_8k,
        'standard_4k': standard_4k,
        'standard_2k': standard_2k,
        'standard_1k': standard_1k,
        'high_fps': high_fps,
        'high_8k': high_8k,
        'high_4k': high_4k,
        'high_2k': high_2k,
        'high_1k': high_1k,
        'full_8k': full_8k,
        'average_fps': average_fps
    }
    
    return result
        

def get_average_allocated_bandwidth(flow_set: dict):
    average_allocated_bandwidth = 0
    for flow in flow_set.values():
        average_allocated_bandwidth += flow['throughput']
    
    average_allocated_bandwidth = average_allocated_bandwidth / len(flow_set)
    return round(average_allocated_bandwidth, 2)

#TODO: this method should use get_route_net_latency and add on top of it the latency of the MEC serverd attached to the last node of the route...
def get_average_e2e_latency(graph, flow_set: dict):
    """ get the average latency of a all paths """
    
    average_e2e_latency = 0
    
    for flow in flow_set.values():
        src_id = flow['client']
        dst_id = flow['server']
        
        source_node_id = str(hmds_set[str(src_id)].current_base_station)
        source_node = base_station_set[source_node_id]
            
        target_mec_id = str(dst_id)
        target_node = base_station_set[target_mec_id]
        
        path, e2e_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
            graph, source_node, target_node
        )
        
        average_e2e_latency += e2e_latency
    
    average_e2e_latency = average_e2e_latency / len(flow_set)
    return round(average_e2e_latency, 2)


def get_average_net_latency(graph, flow_set: dict):
    """ get the average latency of a all paths """
    
    average_net_latency = 0
    
    for flow in flow_set.values():
        flow_route = flow['route']
        flow_route_latency = network_controller.NetworkController.get_route_net_latency(graph, flow_route)
        average_net_latency += flow_route_latency
    
    average_net_latency = average_net_latency / len(flow_set)
    return round(average_net_latency, 2)
        

def get_average_desired_net_latency(graph, flow_set: dict):
    average_net_latency = 0
    
    for flow in flow_set.values():
        src_id = flow['client']
        dst_id = flow['server']
        
        source_node_id = str(hmds_set[str(src_id)].current_base_station)
        source_node = base_station_set[source_node_id]
            
        target_mec_id = str(dst_id)
        target_node = base_station_set[target_mec_id]
        
        path, net_latency = dijkstra_controller.DijkstraController.get_shortest_path(
            graph, source_node, target_node
        )
        
        average_net_latency += net_latency
    
    average_net_latency = average_net_latency / len(flow_set)


def full_resolutions(flow_set: dict) -> bool:
    #result = True
    flow_in_max_throughput = 0
    
    for flow in flow_set.values():
        if flow['throughput'] >= MAX_THROUGHPUT:
           flow_in_max_throughput += 1
    
    logging.info(f'\nFLOWS IN MAX THROUGHPUT: {flow_in_max_throughput} OUT OF {len(flow_set)}\n')
    #return result

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
    floor = 5 # PERCENTAGE
    roof = 20 # PERCENTAGE
    
    percentage = random.uniform(floor, roof)
    num_elements = int(len(flow_set) * (percentage / 100))
    selected_elements = random.sample(flow_set, num_elements)
    
    return selected_elements
    

def get_available_bandwidth_of_node_edges(graph, src: str):
    available_bandwidth = 0
    src_node = graph.graph[src]
    
    for edge in src_node['edges']:
        edge_id = 'BS'+str(edge)
        available_bandwidth += graph.graph[src][edge_id]['available_bandwidth']
        
    return round(available_bandwidth, 2)
    
    
def offload_services(
    base_station_set: Dict[str, 'BaseStation'], mec_set: Dict[str, 'Mec'], hmds_set: Dict[str, 'VrHMD'], graph
):
        count = 0
        for hmd_id, hmd in hmds_set.items():
            for service_id in hmd.services_ids:
                #print(f'\n*** offloading service {service_id} ***')
                #print(f'\nhmd before offloading:')
                #pprint(hmd)
                extracted_service = hmd_controller.HmdController.remove_vr_service(
                    hmd, service_id
                )
                
                #print(f'\nhmd after offloading:')
                #pprint(hmd)
                
                start_node = bs_controller.BaseStationController.get_base_station(
                    base_station_set, hmd.current_base_station
                )

                dst_node: Dict[str, 'Mec'] = mec_controller.MecController.discover_mec(
                    base_station_set, 
                    mec_set, 
                    graph, 
                    start_node, 
                    extracted_service,
                )
                
                dst_mec: 'Mec' = dst_node.get('mec')
                dst_mec_id = dst_node.get('id')

                #print(f'\nmec before offloading:')
                #pprint(dst_mec)
                
                
                if dst_mec is not None:
                    mec_controller.MecController.deploy_service(dst_mec, extracted_service)
                    hmd.offloaded_server = dst_mec_id
                    #pprint(hmd)
                    #a = input('')
                else:
                    count+=1
                    hmd_controller.HmdController.deploy_vr_service(hmds_set, hmd_id, extracted_service)
                    #print(f'\n*** service {extracted_service} could not be offloaded ***')
                #print(f'\nmec after offloading:')
                #pprint(dst_mec)
                
                #a = input('')
        if count > 1:
            print(f'could not offload {count} services')
            #a = input("press any key to continue")


if __name__ == '__main__':
    ### BASE STATIONS ###
    logging.info(f'\n*** decoding base stations ***')
    base_station_set = json_controller.decode_net_config_file()  

    ### MECS ###
    '''
    logging.info(f'\n*** creating mecs ***')
    mec_controller.MecController.create_mec_servers(
        base_station_set, OVERALL_MECS
    )
    '''
   
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
    
    ### SERVICE OFFLOADING ###
    #print(len(graph.graph))
    #print(len(mec_set))

    
    #### ROUTES###
    #route_set = {}

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
                        'route': None,
                        'throughput': bitrate_quotas[first_hmd_quota]['throughput'],
                        'previous_throughput': None,
                        'next_throughput': None,
                }
                pairs += 1
                clients += 1
                video_clients.remove(client) 
        clients = 0   
        video_servers.remove(server)

    #logging.info(f'\n*** initializing route_set ***')
    #network_controller.NetworkController.initialize_route_set(hmds_set, route_set)

    cdn_graph_id = 'BS' + str(CDN_SERVER_ID)
    
    logging.info(f'\n*** starting system ***')

    logging.info(f'updating hmd positions...')
    hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
    logging.info(f'start offloading...')
    offload_services(base_station_set, mec_set, hmds_set, graph)
    
    while True:
        #start = timer()
        flows_order = []
        prioritized_served_flows = [] 
        non_prioritized_served_flows = []

        for i in range(len(flow_set)): 
            if i not in video_servers:
                flows_order.append(i) 
        
        random.shuffle(flows_order)
        
        
        current_throughput = get_current_throughput(flow_set)
        expected_throughput = get_expected_throughput(flow_set)
       
        deallocated_flows_list = []
        
        if ITERATION > 1:
            deallocated_flows_list = flow_fairness_selection(flows_order)  
            
        
        logging.info(f'\n\n################ ITERATION ################\n')
        logging.info(f'ITERATION: {ITERATION}')
        if ITERATION > 1:
            logging.info(f'updating hmd positions...')
            hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
            MIGRATION_ALGORITHM.check_services(base_station_set, mec_set, hmds_set, graph)
            #TODO: need to check if this method is working properly
            
        
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***decallocating route of non-prioritized flows...')
            logging.info(f'{len(deallocated_flows_list)}/{len(flow_set)} flows will be deallocated')
            for flow_id in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                flow = flow_set[flow_id]
                flow_throughput = flow['throughput']
                flow_set[flow_id]['previous_throughput'] = flow_throughput
    
                logging.debug(f'\n dealocating {flow_throughput} Mbps from the following route:')
                logging.debug('->'.join(flow['route']))
                
                network_controller.NetworkController.deallocate_bandwidth(graph, flow_set, flow_id)
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***new CDN edge throughput: {cdn_bandwidth}') 

        
        logging.info(f'\n****************************************************')
        logging.info(f'\n***allocating bandwidth for prioritized flows...')
        
        for flow_id in flows_order:
            if flow_id not in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                flow_throughput = flow['throughput']
                
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
               
                logging.debug(f'\n___________________________________________')
                logging.debug(f'*** \nFLOW ID: {flow_id} *** ') 
                logging.debug(f'\n*** REQUESTING {required_throughput} Mbps ***\n')
                
                flow_set[flow_id]['next_throughput'] = required_throughput
                        
                video_client: VrHMD = hmds_set[str(src_id)]
                source_node_id = video_client.current_base_station
                previous_source_node_id = video_client.previous_base_station
                
                previous_source_node = None
                if previous_source_node_id:
                    previous_source_node = base_station_set[previous_source_node_id]
                
                source_node = base_station_set[source_node_id]

                mec_server = mec_set[str(dst_id)]
                video_server = mec_server.video_server
                video_id = list(video_server.video_set.keys())[0]
                
                manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                
                #pprint(manifest)
                #a = input('')
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                network_controller.NetworkController.deallocate_bandwidth(
                    graph, flow_set, flow_id
                )
                
                if ARG == 'latency_bw_restriction':
                    required_throughput = network_controller.NetworkController.allocate_bandwidth_with_latency_bandwidth_restrictions(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
                elif ARG == 'offloading':
                    source_node_id = str(video_client.offloaded_server)
                    source_node = base_station_set[source_node_id]
                    required_throughput = network_controller.NetworkController.allocate_bandwidth_with_latency_bandwidth_restrictions(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
                else:
                    required_throughput = network_controller.NetworkController.allocate_bandwidth(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
               
                logging.debug(f'\nswitching resolution...\n')
                
                #print(f'requested throughput: {required_throughput} Mbps')
                #pprint(video_client)
                #print(f'\nswitching resolution...\n')
                hmd_controller.HmdController.switch_resolution_based_on_throughput(
                    video_client, manifest, required_throughput
                )
                #pprint(video_client)
                #a = input('')
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                logging.debug(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                
                prioritized_served_flows.append(flow_id)
            
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***reallocating bandwidth for non-prioritized flows...')
            #a = input('')
            flow_count = 0
            for flow_id in deallocated_flows_list:
                logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                flow_count += 1
                
                flow = flow_set[flow_id]
                src_id = flow['client']
                dst_id = flow['server']
                flow_throughput = flow['previous_throughput']
                
                previous_throughput = flow_throughput
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
                flow_set[flow_id]['next_throughput'] = required_throughput
                
                logging.debug(f'\n___________________________________________')
                logging.debug(f'*** \nFLOW ID: {flow_id} - NON-PRIORITIZED ({flow_count}/{len(deallocated_flows_list)})*** ') 
                logging.debug(f'\n*** REQUESTING {required_throughput} Mbps ***')
                logging.debug(f'*** PREVIOUS THROUGHPUT: {previous_throughput} Mbps ***\n')
                            
                video_client: VrHMD = hmds_set[str(src_id)]
                source_node_id = video_client.current_base_station
                previous_source_node_id = video_client.previous_base_station
           
                mec_server = mec_set[str(dst_id)]
                video_server = mec_server.video_server
                video_id = list(video_server.video_set.keys())[0]
                
                manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                if ARG == 'latency_bw_restriction':    
                    required_throughput = network_controller.NetworkController.allocate_bandwidth_with_latency_bandwidth_restrictions(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
                elif ARG == 'offloading':
                    source_node_id = str(video_client.offloaded_server)
                    source_node = base_station_set[source_node_id]
                    required_throughput = network_controller.NetworkController.allocate_bandwidth_with_latency_bandwidth_restrictions(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
                else:
                    required_throughput = network_controller.NetworkController.allocate_bandwidth(
                        graph, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id
                    )
                
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***new CDN edge throughput: {cdn_bandwidth}') 
                
                logging.debug(f'\nswitching resolution...\n')
                
                hmd_controller.HmdController.switch_resolution_based_on_throughput(
                    video_client, manifest, required_throughput
                )
                
                logging.debug(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                
                non_prioritized_served_flows.append(flow_id)
                    
                #a = input('type to process the next flow...')
        
        #end = timer()
        #print(f'\nelapsed time: {end - start}')
        average_net_latency = get_average_net_latency(graph, flow_set)
        averge_e2e_latency = get_average_e2e_latency(graph, flow_set)
        average_allocated_bw = get_average_allocated_bandwidth(flow_set)
        updated_throughput = get_current_throughput(flow_set)
        fps_resoulution = get_fps_resolution(flow_set)
        average_desired_net_latency = get_average_desired_net_latency(graph, flow_set)
        print(f'\n****************************************************\n')
        print(f'PREVIOUS BW: {current_throughput} Mbps')
        print(f'EXPECTED BW: {expected_throughput} Mbps')
        print(f'UPDATED  BW: {updated_throughput} Mbps')
        cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
        print(f'CURRENT AVl. CND BW: {cdn_bandwidth}')
        print(f'AVERAGE NET LATENCY: {average_net_latency} ms')
        print(f'AVERAGE E2E LATENCY: {averge_e2e_latency} ms')
        print(f'AVERAGE BW ALLOCATED: {average_allocated_bw} Mbps')
        pprint(fps_resoulution)
        congestion = calculate_network_overload(graph.graph)
        print(f'CONGESTION: {congestion}')
        
        results_data = []
        results_data.append(congestion)
        results_data.append(current_throughput)
        results_data.append(expected_throughput)
        results_data.append(updated_throughput)
        results_data.append(average_allocated_bw)
        results_data.append(average_net_latency)
        results_data.append(average_desired_net_latency)
        results_data.append(averge_e2e_latency)
        results_data.append(fps_resoulution['average_fps'])
        results_data.append(fps_resoulution['standard_fps'])
        results_data.append(fps_resoulution['standard_8k'])
        results_data.append(fps_resoulution['standard_4k'])
        results_data.append(fps_resoulution['standard_2k'])
        results_data.append(fps_resoulution['standard_1k'])
        results_data.append(fps_resoulution['high_fps'])
        results_data.append(fps_resoulution['high_8k'])
        results_data.append(fps_resoulution['high_4k'])
        results_data.append(fps_resoulution['high_2k'])
        results_data.append(fps_resoulution['high_1k'])
        results_data.append(fps_resoulution['full_8k'])
        
        CSV.save_data(results_dir, FILE_NAME, results_data)
        #full_resolutions(flow_set)
        #generate_networks.plot_graph(graph.graph)
        #time.sleep(1)
       
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



