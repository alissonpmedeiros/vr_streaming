""" controller modules """
from controllers import config_controller
from controllers import bs_controller
from controllers import hmd_controller 
from controllers import json_controller
from controllers import mec_controller
from controllers import graph_controller
from controllers import path_controller
from utils.network import generate_networks 
from controllers import network_controller
from models.bitrates import BitRateProfiles

bitrate_profiles = BitRateProfiles()

import sys

import typing
from typing import Dict
if typing.TYPE_CHECKING:
    from models.mec import Mec
    from models.graph import Graph 
    from models.base_station import BaseStation
    from models.quotas import Quota
    from models.migration_ABC import Migration
    from models.hmd import VrHMD

from models.migration_algorithms.la import LA
'''
from models.migration_algorithms.lra import LRA
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

MIGRATION_ALGORITHM = LA()

MAX_THROUGHPUT = 4153
MIN_THROUGHPUT = 4153


TOPOLOGIES = {
    'bern': {
        'nodes': 147,
        'radius': [0.18, 0.2, 0.22],
        'edges:': [872, 1069, 1263],
        'ALVP':   [5.9, 7.2, 8.5],
        'CDN_SERVER_ID': '45'
    },
    'geneva': {
        'nodes': 269,
        'radius': [0.11, 0.13, 0.15],
        'edges:': [1230, 1692, 2217],
        'ALVP':   [4.5, 6.2, 8.24],
        'CDN_SERVER_ID': '49'
    },
    'zurich': {
        'nodes': 586,
        'radius': [0.08, 0.09, 0.1],
        'edges:': [3173, 3996, 4868],
        'ALVP':   [5.4, 6.8, 8.3],
        'CDN_SERVER_ID': '455'
    }
}


### CONFIG ###

CONFIG = config_controller.ConfigController.get_config()
json_controller = json_controller.DecoderController()

CITY_TOPOLOGY = CONFIG['SYSTEM']['CITY_TOPOLOGY']
TOPOLOGY_RADIUS = CONFIG['SYSTEM']['TOPOLOGY_RADIUS']

data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
mecs_file = CONFIG['SYSTEM']['MEC_FILE']
results_dir = CONFIG['SYSTEM']['RESULTS_DIR']

new_radius = str(TOPOLOGY_RADIUS)
new_radius = new_radius.replace('.', '_')
results_dir = "{}{}/r_{}/".format(results_dir, CITY_TOPOLOGY, new_radius)

ITERATION = 1

OVERALL_MECS = CONFIG['MEC_SERVERS']['OVERALL_MECS']
OVERALL_VIDEO_SERVERS = 1
OVERALL_VIDEO_CLIENTS = CONFIG['NETWORK']['HMDS']
#OVERALL_VIDEO_CLIENTS = 5
CLIENTS_PER_SERVER = OVERALL_VIDEO_CLIENTS / OVERALL_VIDEO_SERVERS

CDN_SERVER_ID = TOPOLOGIES[CITY_TOPOLOGY]['CDN_SERVER_ID']
CDN_CLIENT_ID = 161

'''
net_file_dir = CONFIG['NETWORK']['NETWORK_FILE_DIR']

network_controller.NetworkController.reduce_edge_net_latencies(net_file_dir, 'network.json')
a = input('')
'''

#FILE_NAME = 'bandwidth.csv'
ROUTING_ALGORITHM = sys.argv[1]
FILE_NAME = '{}.csv'.format(ROUTING_ALGORITHM)

FILE_HEADER = [
    'city_topology',
    'topology_radius',
    'routing_algorithm',
    'net_congestion',
    'total_net_throughput',
    'flow_e2e_latency', 
    'fow_throughput',
    'flow_latency', 
    'route_latency',
    'overp_net_latency',
    'impaired_services',
    'execution_time',
    'fps',
    'weak_4k',
    'weak_8k',
    'weak_12k',
    'weak_24k',
    'strong_4k',
    'strong_8k',
    'strong_12k',
    'strong_24k',
    'full_24k'
]

CSV.create_file(results_dir, FILE_NAME, FILE_HEADER)    

def get_total_throughput(flow_set: dict):
    overall_throughput = 0
    for flow in flow_set.values():
        flow_quota = flow['current_quota']
        overall_throughput += flow_quota['throughput']
        
    return round(overall_throughput / 1024, 2)

def calculate_network_congestion(graph):
    
    congested_links = 0
    total_links = 0

    visited_nodes = []
    for node, node_data in graph.items():
        for neighbor, neighbor_data in node_data.items():
            if neighbor.startswith('BS') and neighbor not in visited_nodes:
                total_links += 1
                if neighbor_data['available_bandwidth'] < MIN_THROUGHPUT:
                    congested_links += 1
                visited_nodes.append(neighbor)
        visited_nodes.append(node)

    congestion_level = (congested_links * total_links) / 100
    
    
    return round(congestion_level, 2)

def get_resolutions(flow_set: dict):
    
    weak_24k = 0 
    weak_12k = 0 
    weak_8k = 0 
    week_4k = 0
    
    strong_24k = 0
    strong_12k = 0
    strong_8k = 0
    strong_4k = 0
    
    full_24k = 0
    
    for flow in flow_set.values():
        flow_throughput = flow['current_quota']
        flow_throughput = flow_throughput['throughput']
        #  	Video Bitrate for 4k weak interaction
        if flow_throughput >= 25 and flow_throughput < 50:
            week_4k += 1
            
        # Video Bitrate for 4k strong interaction 
        elif flow_throughput >= 50 and flow_throughput < 63:
            strong_4k += 1
            
        #  	Video Bitrate for 8k weak interaction
        elif flow_throughput >= 63 and flow_throughput < 200:
            weak_8k += 1
            
        # Video Bitrate for 8k strong interaction
        elif flow_throughput >= 200 and flow_throughput < 304:
            strong_8k += 1
                
        #  	Video Bitrate for 12k weak interaction
        elif flow_throughput >= 304 and flow_throughput < 1424:
            weak_12k += 1
            
        # Video Bitrate for 12k strong interaction
        elif flow_throughput >= 1424 and flow_throughput < 2388:
            strong_12k += 1
            
        #  	Video Bitrate for 24k weak interaction
        elif flow_throughput >= 2388 and flow_throughput < 3432:
            weak_24k += 1
            
        # Video Bitrate for 24k strong interaction
        elif flow_throughput >= 3432 and flow_throughput <= 4153:
            strong_24k += 1
            if flow_throughput == 4153:
                full_24k += 1
    
    result = {
        'weak_24k': weak_24k,
        'weak_12k': weak_12k,
        'weak_8k': weak_8k,
        'weak_4k': week_4k,
        'strong_24k': strong_24k,
        'strong_12k': strong_12k,
        'strong_8k': strong_8k,
        'strong_4k': strong_4k,
        'full_24k': full_24k,
    }
    
    return result
        
#TODO: this method should use get_route_net_latency and add on top of it the latency of the MEC serverd attached to the last node of the route...
def get_average_e2e_latency(graph, flow_set: dict):
    """ get the average latency of a all paths """
    
    average_e2e_latency = 0
    
    for flow in flow_set.values():
        src_id = flow['client']
        dst_id = flow['server']
        flow_route = flow['route']
        
        source_node_id = str(hmds_set[str(src_id)].current_base_station)
        source_node: 'BaseStation' = base_station_set[source_node_id]
        
        route_latency = network_controller.NetworkController.get_route_net_latency(graph, flow_route)
        
        
        average_e2e_latency += (source_node.node_latency + source_node.wireless_latency + route_latency)
    
    average_e2e_latency = average_e2e_latency / len(flow_set)
    return round(average_e2e_latency, 2)

def get_average_resolution_fps(flow_set: dict):
    average_fps = 0
    for flow in flow_set.values():
        flow_quota = flow['current_quota']
        average_fps += flow_quota['frame_rate']
        
    return round(average_fps / len(flow_set), 2)

def get_average_resolution_throughput(flow_set: dict):
    average_throughput = 0
    for flow in flow_set.values():
        flow_quota = flow['current_quota']
        average_throughput += flow_quota['throughput']
        
    return round((average_throughput / 1024) / len(flow_set), 2)

def get_average_resolution_latency(flow_set: dict):
    average_latency = 0
    for flow in flow_set.values():
        flow_quota = flow['current_quota']
        average_latency += flow_quota['latency']
        
    return round(average_latency / len(flow_set), 2)

def get_average_route_latency(graph, flow_set: dict):
    average_route_latency = 0
    for flow in flow_set.values():
        flow_route = flow['route']
        
        average_route_latency += network_controller.NetworkController.get_route_net_latency(graph, flow_route)
    
    return round(average_route_latency / len(flow_set), 2)
        

def flow_fairness_selection(flow_order):
    """ return a list of flows that will be not prioritized """
    floor = 5 # PERCENTAGE
    roof = 20 # PERCENTAGE
    
    percentage = random.uniform(floor, roof)
    num_elements = int(len(flow_order) * (percentage / 100))
    selected_elements = random.sample(flow_order, num_elements)
    
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

            #pprint(dst_node)
            #a = input('')
            #print(f'\nmec before offloading:')
            #pprint(dst_mec)
            
            
            if dst_mec is not None:
                mec_controller.MecController.deploy_service(dst_mec, extracted_service)
                hmd.offloaded_server = dst_mec_id
                hmd.service_offloading = True
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
        a = input("press any key to continue")


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
    # logging.info(f'\n*** creating hmds ***')
    # hmd_controller.HmdController.create_hmds()

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

    
    logging.info(f'\n*** creating video and client servers ***')
    
    
    bitrate_quotas = bitrate_profiles.get_bitrate_quota_profiles()
    for hmd_id, hmd in hmds_set.items():
        hmd_quota = hmd.services_set[0].quota.name
        flow_set[int(hmd_id)] = {
                'server': int(CDN_SERVER_ID),
                'client': int(hmd_id),
                'route': None,
                'current_quota_name': hmd_quota,
                'current_quota': bitrate_quotas[hmd_quota],
                'previous_quota_name': None,
                'previous_quota': None,
                'next_quota_name': None,
                'next_quota': None,
        }
        

    #logging.info(f'\n*** initializing route_set ***')
    #network_controller.NetworkController.initialize_route_set(hmds_set, route_set)

    cdn_graph_id = 'BS' + str(CDN_SERVER_ID)
    
    logging.info(f'\n*** starting system ***')

    # if ROUTING_ALGORITHM == 'flatwise':
    #     logging.info(f'updating hmd positions...')
    #     hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
    #     logging.info(f'offloading services...')
    #     offload_services(base_station_set, mec_set, hmds_set, graph)
    """
        for mec in mec_set.values():
            print(f'{mec.name} -> {mec.allocated_cpu}({mec.overall_cpu}) | {mec.allocated_gpu}({mec.overall_gpu})')
        
        a = input('')
    """    
        
        
        
    
    
    flows_order = []
    for i in range(len(flow_set)): 
        flows_order.append(i) 
    
    
    while True:
        execution_time = 0
        impaired_services = {'services': 0}
        
        random.shuffle(flows_order)
        prioritized_served_flows = [] 
        non_prioritized_served_flows = []
       
        deallocated_flows_list = []
        
        if ITERATION > 1:
            deallocated_flows_list = flow_fairness_selection(flows_order)  
            
        
        logging.info(f'\n\n################ ITERATION ################\n')
        logging.info(f'ITERATION: {ITERATION}')
        
        logging.info(f'updating hmd positions...')
        hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set, CDN_SERVER_ID)
        
        # if ITERATION > 1 and ROUTING_ALGORITHM == 'flatwise':        
        #     logging.info(f'checking service migration...')
        #     MIGRATION_ALGORITHM.check_services(base_station_set, mec_set, hmds_set, graph)
            
            
        
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***decallocating route of non-prioritized flows...')
            logging.info(f'{len(deallocated_flows_list)}/{len(flow_set)} flows will be deallocated')
            for flow_id in deallocated_flows_list:
                #logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge current_quota: {cdn_bandwidth}') 
                
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                flow = flow_set[flow_id]
                flow_quota = flow['current_quota']
                flow_quota_name = flow['current_quota_name']
                
                flow_set[flow_id]['previous_quota'] = flow_quota
                flow_set[flow_id]['previous_quota_name'] = flow_quota_name

                #logging.info(f'\n dealocating {flow_quota} Mbps from the following route:')
                
                #logging.info('->'.join(flow['route']))
                
                network_controller.NetworkController.deallocate_bandwidth(graph, flow_set, flow_id)
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***new CDN edge current_quota: {cdn_bandwidth}') 

        
        logging.info(f'\n****************************************************')
        logging.info(f'\n***allocating bandwidth for prioritized flows...')
        
        for flow_id in flows_order:
            if flow_id not in deallocated_flows_list:
                #logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge current_quota: {cdn_bandwidth}') 
                
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                
                flow_quota = flow['current_quota']
                flow_quota_name = flow['current_quota_name']
                
                required_quota_name, required_quota = bitrate_profiles.get_next_bitrate_quota(flow_quota_name)
                
               
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                #logging.info(f'\n*** REQUESTING {required_quota} Mbps ***\n')
                #pprint(flow)
                
                flow_set[flow_id]['next_quota'] = required_quota
                flow_set[flow_id]['next_quota_name'] = required_quota_name
                        
                video_client: 'VrHMD' = hmds_set[str(src_id)]
                source_node_id = video_client.current_base_station
                previous_source_node_id = video_client.previous_base_station
                
                previous_source_node = None
                if previous_source_node_id:
                    previous_source_node = base_station_set[previous_source_node_id]
                
                source_node = base_station_set[source_node_id]

                # mec_server = mec_set[str(dst_id)]
                # video_server = mec_server.video_server
                # video_id = list(video_server.video_set.keys())[0]
                
                # manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                network_controller.NetworkController.deallocate_bandwidth(
                    graph, flow_set, flow_id
                )
                
                start = timer()
                network_controller.NetworkController.allocate_bandwidth(
                    base_station_set, graph, ROUTING_ALGORITHM, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id, impaired_services
                )
                end = timer()
                execution_time += end - start
                # logging.debug(f'\nswitching resolution...\n')
                
                #print(f'requested current_quota: {required_quota} Mbps')
                #pprint(video_client)
                #print(f'\nswitching resolution...\n')
                # hmd_controller.HmdController.switch_resolution_based_on_current_quota(
                #     video_client, manifest, required_quota
                # )
                #pprint(video_client)
                #a = input('')
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge current_quota: {cdn_bandwidth}') 
                
                #logging.info(f'\nFINAL FLOW REQUEST OF {required_quota} Mbps from {src_id} -> {dst_id}')
                
                #pprint(flow)
                
                #a = input('')
                
                prioritized_served_flows.append(flow_id)
        
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***reallocating bandwidth for non-prioritized flows...')
            #a = input('')
            flow_count = 0
            for flow_id in deallocated_flows_list:
                #logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge current_quota: {cdn_bandwidth}') 
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                
                flow_count += 1
                
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                
                flow_quota = flow['current_quota']
                flow_quota_name = flow['current_quota_name']
                
                # previous_quota = flow_quota
                
                
                required_quota_name, required_quota = bitrate_profiles.get_next_bitrate_quota(flow_quota_name)
                
                flow_set[flow_id]['next_quota'] = required_quota
                flow_set[flow_id]['next_quota_name'] = required_quota_name
                
                #logging.debug(f'\n___________________________________________')
                #logging.debug(f'*** \nFLOW ID: {flow_id} - NON-PRIORITIZED ({flow_count}/{len(deallocated_flows_list)})*** ') 
                #logging.debug(f'\n*** REQUESTING {required_quota} Mbps ***')
                #logging.debug(f'*** PREVIOUS THROUGHPUT: {previous_current_quota} Mbps ***\n')
                            
                # video_client: 'VrHMD' = hmds_set[str(src_id)]
                # source_node_id = video_client.current_base_station
                # previous_source_node_id = video_client.previous_base_station
           
                # mec_server = mec_set[str(dst_id)]
                # video_server = mec_server.video_server
                # video_id = list(video_server.video_set.keys())[0]
                
                # manifest = hmd_controller.HmdController.request_manifest(mec_set, video_id)
                    
                target_mec_id = str(dst_id)
                target_node = base_station_set[target_mec_id]
                
                start = timer()
                network_controller.NetworkController.allocate_bandwidth(
                    base_station_set, graph, ROUTING_ALGORITHM, source_node, target_node, flow_set, prioritized_served_flows, non_prioritized_served_flows, flow_id, impaired_services
                )
                end = timer()
                execution_time += end - start
                
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***new CDN edge current_quota: {cdn_bandwidth}') 
                
                logging.debug(f'\nswitching resolution...\n')
                
                # hmd_controller.HmdController.switch_resolution_based_on_current_quota(
                #     video_client, manifest, required_quota
                # )
                
                logging.debug(f'\nFINAL FLOW REQUEST OF {required_quota} Mbps from {src_id} -> {dst_id}')
                
                non_prioritized_served_flows.append(flow_id)
                    
                #a = input('type to process the next flow...')
        
        
        if ITERATION > 2:
            average_net_congestion = calculate_network_congestion(graph.graph)
            average_total_net_throughput = get_total_throughput(flow_set)
            average_flow_e2e_latency = get_average_e2e_latency(graph, flow_set)
            average_flow_throughput = get_average_resolution_throughput(flow_set)
            average_flow_latency = get_average_resolution_latency(flow_set)
            average_route_latency = get_average_route_latency(graph, flow_set)
            average_impaired_services = impaired_services['services']
            average_overprovisioned_net_latency = round(average_flow_latency - average_route_latency, 2)
            average_execution_time = round(execution_time, 2) 
            average_fps = get_average_resolution_fps(flow_set)
            resolutions = get_resolutions(flow_set)
                
            results_data = []
            results_data.append(CITY_TOPOLOGY)
            results_data.append(TOPOLOGY_RADIUS)
            results_data.append(ROUTING_ALGORITHM)
            results_data.append(average_net_congestion)
            results_data.append(average_total_net_throughput)
            results_data.append(average_flow_e2e_latency)
            results_data.append(average_flow_throughput)
            results_data.append(average_flow_latency)
            results_data.append(average_route_latency)
            results_data.append(average_overprovisioned_net_latency)
            results_data.append(average_impaired_services)
            results_data.append(average_execution_time)
            results_data.append(average_fps)
            results_data.append(resolutions['weak_4k'])
            results_data.append(resolutions['weak_8k'])
            results_data.append(resolutions['weak_12k'])
            results_data.append(resolutions['weak_24k'])
            results_data.append(resolutions['strong_4k'])
            results_data.append(resolutions['strong_8k'])
            results_data.append(resolutions['strong_12k'])
            results_data.append(resolutions['strong_24k'])
            results_data.append(resolutions['full_24k'])
        
            CSV.save_data(results_dir, FILE_NAME, results_data)
            # a = input('')
        
       
        ITERATION += 1
    
















""" 
if __name__ == '__main__':
    
    
    while True:
        quota = bitrate_profiles.get_bitrate_quota(4, 4000)
        print(quota)
        a = input('\npress to continue!\n')
    
    # logging.info(f'\n*** decoding base stations ***')
    base_station_set = json_controller.decode_net_config_file() 
    
    
    # logging.info(f'\n*** building network graph ***')
    graph = graph_controller.GraphController.get_graph(base_station_set)
    # generate_networks.plot_graph(graph.graph)
    # a = input('')
     
    # while True:
    #    generate_networks.plot_graph(graph.graph)
    #    time.sleep(5)

    # source_node = base_station_set['4']
    # target_node = base_station_set['8']
    
    source_node = base_station_set['17']
    target_node = base_station_set['18']
    
    
    
    it = 0
    
    # while True:
    #     it += 1
    #     src = str(random.randint(1, 260))
    #     dst = str(random.randint(1, 260))
    #     while src == dst:
    #         dst = str(random.randint(1, 260))   
    
    #     source_node = base_station_set[src]
    #     target_node = base_station_set[dst]
        
    #     required_quota = 10
        
    #     for i in range(3, 11):
        
    #         latency_requirement = i
    #         path, cost = path_controller.PathController.get_flatwise_path(base_station_set, graph, source_node, target_node, latency_requirement, required_quota)
            
    #         widest_current_quota = network_controller.NetworkController.get_route_widest_current_quota(graph, path)
    #         print(f'\nroute found with cost {widest_current_quota} Mbps ({cost} ms)')
    #         print(" -> ".join(path))
        
    #     a = input('')
        
        # paths = path_controller.PathController.get_shortest_widest_path(graph, source_node, target_node, 10)
        
        
        # if len(paths) > 1:
        #     print(f'\niteration {it}\n')
        #     print(f'___________________________')
        #     for path in paths:
        #         print(path)
        #         route_latency = network_controller.NetworkController.get_route_net_latency(graph, path[0])
        #         print(round(route_latency, 2))
        #         print(f'\n')
                
        #     print(f'___________________________')
            
        #     swp_path, swp_cost = get_SWP(paths)
        #     route_latency = network_controller.NetworkController.get_route_net_latency(graph, swp_path)
        #     print(f'\nselected path with cost {route_latency} ms and current_quota {swp_cost} Mbps')
        #     print(swp_path)
            
        #     a = input('')
        
        
        # paths = path_controller.PathController.get_widest_shortest_path(graph, source_node, target_node, 10)
        
        
        # if len(paths) > 1:
        #     print(f'\niteration {it}\n')
        #     print(f'___________________________')
        #     for path in paths:
        #         print(path)
        #         route_current_quota = network_controller.NetworkController.get_route_net_current_quota(graph, path[0])
        #         print(round(route_current_quota, 2))
        #         print(f'\n')
                
        #     print(f'___________________________')
            
        #     wsp_path, wsp_cost = get_WSP(paths)
        #     route_current_quota = network_controller.NetworkController.get_route_net_current_quota(graph, wsp_path)
        #     print(f'\nselected path with cost {wsp_cost} ms and current_quota {route_current_quota} Mbps')
        #     print(wsp_path)
            
        #     a = input('')
        
        
"""