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
from itertools import tee
bitrate_profiles = BitRateProfiles()

import sys, math, heapq

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
    if total_standard_fps > 0:
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
        
        path, e2e_latency = path_controller.DijkstraController.get_ETE_shortest_path(
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
        
        if ARG == 'offloading':
            src_id = flow['client']
            flow_hmd = hmds_set[str(src_id)]
            source_node_id = str(flow_hmd.current_base_station)
            source_node = base_station_set[source_node_id]
            
            target_mec_id = str(flow_hmd.offloaded_server)
            target_node = base_station_set[target_mec_id]
            
            path, net_latency_from_hmd_to_offloaded_mec = path_controller.DijkstraController.get_shortest_path(
                graph, source_node, target_node
            )
            
            '''
            print(f'route latency: {flow_route_latency}')
            print(' -> '.join(flow_route))
            print(f'\nhmd to offloaded mec: {net_latency_from_hmd_to_offloaded_mec}')
            print(' -> '.join(path))
            a = input('')
            '''
            
            flow_route_latency += net_latency_from_hmd_to_offloaded_mec
        
        average_net_latency += flow_route_latency
    
    average_net_latency = average_net_latency / len(flow_set)
    return round(average_net_latency, 2)
        

def get_average_desired_net_latency(graph, flow_set: dict):
    average_net_latency = 0
    #print(f'\n*** getting average desired net latency ***\n')
    for flow in flow_set.values():
        src_id = flow['client']
        dst_id = flow['server']
        
        source_node_id = str(hmds_set[str(src_id)].current_base_station)
        source_node = base_station_set[source_node_id]
            
        target_mec_id = str(dst_id)
        target_node = base_station_set[target_mec_id]
        
        path, net_latency = path_controller.DijkstraController.get_shortest_path(
            graph, source_node, target_node
        )
        average_net_latency += net_latency
    
    average_net_latency = average_net_latency / len(flow_set)
    return round(average_net_latency, 2)


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


def euclidean_distance(node, goal_node):
    x1, y1 = node.position[0], node.position[1]
    x2, y2 = goal_node.position[0], goal_node.position[1]
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)    
    return distance




def normalize(value, min_val, max_val):
    normalized_value = (value - min_val) / (max_val - min_val)
    return normalized_value

def ER6VA(node: 'BaseStation', goal_node: 'BaseStation', predecessor: str, graph: 'Graph') -> float:
    
    # Get the network throughput and congestion level of the edge from node to goal_node
    throughput = graph.get_network_available_throughput(node.bs_name, predecessor)
    latency = graph.get_network_latency(node.bs_name, predecessor)
    congestion = graph.get_link_congestion_level(node.bs_name, predecessor)
    
    
    # Compute the geographical distance between node and goal_node (e.g., using their (x, y) coordinates)
    x1, y1 = node.position[0], node.position[1]
    x2, y2 = goal_node.position[0], goal_node.position[1]
    
    # Calculate Euclidean distance
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
def pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)







# # Heuristic function
# def heuristic(node, goal_node, predecessor):
#     #the throughput and latency between the node and its predecessor are calculated as follows 
#     throughput = graph.get_network_available_throughput(node.bs_name, predecessor)
#     latency = graph.get_network_latency(node.bs_name, predecessor)
#     congestion = graph.get_link_congestion_level(node.bs_name, predecessor)
    
#     # Assuming nodes have x and y coordinates
#     x1, y1 = node.position[0], node.position[1]
#     x2, y2 = goal_node.position[0], goal_node.position[1]
    
#     # Calculate Euclidean distance
#     distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
#     return distance

# def FLATWISE(graph: 'Graph', base_station_set: Dict[str, 'BaseStation'],  start_node: 'BaseStation', goal_node: 'BaseStation'):
#         initial_distance = euclidean_distance(source_node, target_node)
#         latency_requirement = 10
#         achieved_latency = 0
#         desired_latency = 0
        
#         unvisited_nodes = set(graph.get_nodes())
#         dist = {}
#         previous_nodes = {}
        
#         max_value = sys.maxsize
#         for node in unvisited_nodes:
#             dist[node] = max_value
        
#         dist[start_node.bs_name] = 0
        
#         # Priority queue for open nodes
#         open_nodes = [(dist[start_node.bs_name] + heuristic(start_node, goal_node, predecessor=None), start_node.bs_name)]
#         it = 0
#         while open_nodes:
            
#             _, current_node = heapq.heappop(open_nodes)
#             current_node_bs = base_station_set[current_node[2:]]
#             current_distance = euclidean_distance(current_node_bs, goal_node)
#             current_percentage = (current_distance * 100) / initial_distance
#             # print(f'current node {current_node} is {current_percentage}% away from goal node {goal_node.bs_name}')
#             # pprint(open_nodes)
#             # a = input('')
#             if current_node == goal_node.bs_name:
#                 break
            
#             if current_node in unvisited_nodes:
#                 unvisited_nodes.remove(current_node)
                
#                 neighbors = graph.get_outgoing_edges(current_node)
#                 for neighbor in neighbors:
#                     if neighbor in unvisited_nodes:
#                         it += 1
#                         new_distance = dist[current_node] + graph.get_network_latency(current_node, neighbor)
#                         if new_distance < dist[neighbor]:
#                             dist[neighbor] = new_distance
#                             previous_nodes[neighbor] = current_node
#                             neighbor_bs = base_station_set[neighbor[2:]]
#                             # pprint(neighbor_bs)
#                             # a = input('')
#                             heapq.heappush(open_nodes, (new_distance + heuristic
#                         (neighbor_bs, goal_node, predecessor=current_node), neighbor))
#                             # heapq.heappush(open_nodes, (new_distance + ER6VA(neighbor_bs, goal_node, current_node, graph), neighbor))
                
                
#                 # pprint(open_nodes)
#                 # for neighbor in neighbors:
#                 #     print(f'dist[{neighbor}]: {dist[neighbor]}')
#                 # a = input()
                
#                 # pprint(open_nodes)
#                 # a = input('')
        
#         #pprint(dist)
#         #pprint(previous_nodes)
#         # print(f'\n***iterations: {it}\n')
#         return previous_nodes, dist



def A_estrela_bk(graph: 'Graph', base_station_set: Dict[str, 'BaseStation'],  start_node: 'BaseStation', goal_node: 'BaseStation'):
        unvisited_nodes = set(graph.get_nodes())
        dist = {}
        previous_nodes = {}
        
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
        
        dist[start_node.bs_name] = 0
        
        # Heuristic function
        def heuristic(node, goal_node):
            # Assuming nodes have x and y coordinates
            x1, y1 = node.position[0], node.position[1]
            x2, y2 = goal_node.position[0], goal_node.position[1]
            
            # Calculate Euclidean distance
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            return distance
        
        # Priority queue for open nodes
        open_nodes = [(dist[start_node.bs_name] + heuristic(start_node, goal_node), start_node.bs_name)]
        it = 0
        while open_nodes:
            # print(open_nodes)
            # a = input('')
            _, current_node = heapq.heappop(open_nodes)
            
            if current_node == goal_node.bs_name:
                break
            
            if current_node in unvisited_nodes:
                unvisited_nodes.remove(current_node)
                
                neighbors = graph.get_outgoing_edges(current_node)
                for neighbor in neighbors:
                    if neighbor in unvisited_nodes:
                        it += 1
                        new_distance = dist[current_node] + graph.get_network_latency(current_node, neighbor)
                        if new_distance < dist[neighbor]:
                            dist[neighbor] = new_distance
                            previous_nodes[neighbor] = current_node
                            neighbor_bs = base_station_set[neighbor[2:]]
                            heapq.heappush(open_nodes, (new_distance + heuristic(neighbor_bs, goal_node), neighbor))
        
        #pprint(dist)
        #pprint(previous_nodes)
        # print(f'\n***iterations: {it}\n')
        return previous_nodes, dist

def calculate_shortest_path( 
        previous_nodes, shortest_path, start_node: 'BaseStation', target_node: 'BaseStation'
    ):
        """ returns the shortest path (lowest ETE latency) between the source and destination node and the path cost """
        path = []
        node = target_node.bs_name
        
        while node != start_node.bs_name:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
    
        """ Adds the start node manually """
        path.append(start_node.bs_name)
        
        path.reverse()
        return path, round(shortest_path[target_node.bs_name], 2)



""" 
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

    
    logging.info(f'\n*** creating video and client servers ***')
    
    '''
    for server in video_servers.copy():
        for client in video_clients.copy():
            if clients == CLIENTS_PER_SERVER:
                break
            else:
                mec_id = str(server)
                bitrate_quotas = bitrate_profiles.get_bitrate_quota_profiles()
                hmd_quota = hmds_set[str(client)].services_set[0].quota.name
                flow_set[pairs] = {
                        'server': server,
                        'client': client,
                        'route': None,
                        'throughput': bitrate_quotas[hmd_quota]['throughput'],
                        'previous_throughput': None,
                        'next_throughput': None,
                }
                pairs += 1
                clients += 1
                video_clients.remove(client) 
        clients = 0   
        video_servers.remove(server)
    '''
    
    bitrate_quotas = bitrate_profiles.get_bitrate_quota_profiles()
    for hmd_id, hmd in hmds_set.items():
        hmd_quota = hmd.services_set[0].quota.name
        flow_set[int(hmd_id)] = {
                'server': int(CDN_SERVER_ID),
                'client': int(hmd_id),
                'route': None,
                'throughput': bitrate_quotas[hmd_quota]['throughput'],
                'previous_throughput': None,
                'next_throughput': None,
        }
        

    #logging.info(f'\n*** initializing route_set ***')
    #network_controller.NetworkController.initialize_route_set(hmds_set, route_set)

    cdn_graph_id = 'BS' + str(CDN_SERVER_ID)
    
    logging.info(f'\n*** starting system ***')

    if ARG == 'offloading':
        logging.info(f'updating hmd positions...')
        hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
        logging.info(f'offloading services...')
        offload_services(base_station_set, mec_set, hmds_set, graph)
        
        '''
        for mec in mec_set.values():
            print(f'{mec.name} -> {mec.allocated_cpu}({mec.overall_cpu}) | {mec.allocated_gpu}({mec.overall_gpu})')
        
        a = input('')
        '''
        
        
    
    '''
    for flow_id, flow in flow_set.items():
        if flow['client'] == 0:            
            print(f'\nroute for hmd 0')
            #print('->'.join(flow['route']))
            pprint(f'flow id: {flow_id}')
        if flow['client'] == 1: 
            print(f'\nroute for hmd 1')
            #print('->'.join(flow['route']))
            pprint(f'flow id: {flow_id}')
        if flow['client'] == 2: 
            print(f'\nroute for hmd 2')
            #print('->'.join(flow['route']))
            pprint(f'flow id: {flow_id}')
    
    '''
    flows_order = []
    for i in range(len(flow_set)): 
        flows_order.append(i) 
        #if i not in video_servers:
            #flows_order.append(i) 
    
    
    while True:
        #start = timer()
        #pprint(flow_set)
        #a = input('')
        random.shuffle(flows_order)
        prioritized_served_flows = [] 
        non_prioritized_served_flows = []
        
        
        current_throughput = get_current_throughput(flow_set)
        expected_throughput = get_expected_throughput(flow_set)
       
        deallocated_flows_list = []
        
        if ITERATION > 1:
            deallocated_flows_list = flow_fairness_selection(flows_order)  
            
        
        logging.info(f'\n\n################ ITERATION ################\n')
        logging.info(f'ITERATION: {ITERATION}')
        
        logging.info(f'updating hmd positions...')
        hmd_controller.HmdController.update_hmd_positions(base_station_set, hmds_set)
        
        if ITERATION > 1 and ARG == 'offloading':
            '''
           
            print(f'\nroute for hmd 0')
            print('->'.join(flow_set[0]["route"]))
            
            print(f'\nroute for hmd 1')
            print('->'.join(flow_set[1]["route"]))
            
            print(f'\nroute for hmd 2')
            print('->'.join(flow_set[2]["route"]))
            
           '''
                    
            logging.info(f'checking service migration...')
            MIGRATION_ALGORITHM.check_services(base_station_set, mec_set, hmds_set, graph)
            #TODO: need to check if this method is working properly
            
        
        if ITERATION > 1:
            logging.info(f'\n****************************************************')
            logging.info(f'\n***decallocating route of non-prioritized flows...')
            logging.info(f'{len(deallocated_flows_list)}/{len(flow_set)} flows will be deallocated')
            for flow_id in deallocated_flows_list:
                #logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                flow = flow_set[flow_id]
                flow_throughput = flow['throughput']
                flow_set[flow_id]['previous_throughput'] = flow_throughput
    
                #logging.info(f'\n dealocating {flow_throughput} Mbps from the following route:')
                
                #logging.info('->'.join(flow['route']))
                
                network_controller.NetworkController.deallocate_bandwidth(graph, flow_set, flow_id)
                
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***new CDN edge throughput: {cdn_bandwidth}') 

        
        logging.info(f'\n****************************************************')
        logging.info(f'\n***allocating bandwidth for prioritized flows...')
        
        for flow_id in flows_order:
            if flow_id not in deallocated_flows_list:
                #logging.debug(f'\n______________________________________________________')
                #cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                
                flow = flow_set[flow_id]
                
                src_id = flow['client']
                dst_id = flow['server']
                flow_throughput = flow['throughput']
                
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
               
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                #logging.info(f'\n*** REQUESTING {required_throughput} Mbps ***\n')
                #pprint(flow)
                
                flow_set[flow_id]['next_throughput'] = required_throughput
                        
                video_client: 'VrHMD' = hmds_set[str(src_id)]
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
                
                #logging.info(f'\nFINAL FLOW REQUEST OF {required_throughput} Mbps from {src_id} -> {dst_id}')
                
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
                #logging.debug(f'\n***current CND edge throughput: {cdn_bandwidth}') 
                #logging.info(f'\n___________________________________________')
                #logging.info(f'*** \nFLOW ID: {flow_id} *** ') 
                
                flow_count += 1
                
                flow = flow_set[flow_id]
                src_id = flow['client']
                dst_id = flow['server']
                flow_throughput = flow['previous_throughput']
                
                previous_throughput = flow_throughput
                required_throughput = bitrate_profiles.get_next_throughput_profile(flow_throughput)
                flow_set[flow_id]['next_throughput'] = required_throughput
                
                #logging.debug(f'\n___________________________________________')
                #logging.debug(f'*** \nFLOW ID: {flow_id} - NON-PRIORITIZED ({flow_count}/{len(deallocated_flows_list)})*** ') 
                #logging.debug(f'\n*** REQUESTING {required_throughput} Mbps ***')
                #logging.debug(f'*** PREVIOUS THROUGHPUT: {previous_throughput} Mbps ***\n')
                            
                video_client: 'VrHMD' = hmds_set[str(src_id)]
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
        #pprint(flow_set)
        #a = input('')
        average_net_latency = get_average_net_latency(graph, flow_set)
        averge_e2e_latency = get_average_e2e_latency(graph, flow_set)
        average_allocated_bw = get_average_allocated_bandwidth(flow_set)
        updated_throughput = get_current_throughput(flow_set)
        fps_resoulution = get_fps_resolution(flow_set)
        average_desired_net_latency = get_average_desired_net_latency(graph, flow_set)
        congestion = calculate_network_overload(graph.graph)
        cdn_bandwidth = get_available_bandwidth_of_node_edges(graph, cdn_graph_id)
        #print(f'\n****************************************************\n')
        #print(f'average net latency: {average_net_latency} ms')
        #print(f'desired net latency: {average_desired_net_latency} ms')
        #time.sleep(3)
        
        '''
        print(f'PREVIOUS BW: {current_throughput} Mbps')
        print(f'EXPECTED BW: {expected_throughput} Mbps')
        print(f'UPDATED  BW: {updated_throughput} Mbps')
        print(f'CURRENT AVl. CND BW: {cdn_bandwidth}')
        print(f'AVERAGE NET LATENCY: {average_net_latency} ms')
        print(f'AVERAGE E2E LATENCY: {averge_e2e_latency} ms')
        print(f'AVERAGE BW ALLOCATED: {average_allocated_bw} Mbps')
        pprint(fps_resoulution)
        print(f'CONGESTION: {congestion}')
        '''
        
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
"""




if __name__ == '__main__':
    
    
    while True:
        quota = bitrate_profiles.get_bitrate_quota(6, 4000)
        print(quota)
        a = input('\npress to continue!\n')
    
    a = input('press to quit!')
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
    """
    while True:
        it += 1
        src = str(random.randint(1, 260))
        dst = str(random.randint(1, 260))
        while src == dst:
            dst = str(random.randint(1, 260))   
    
        source_node = base_station_set[src]
        target_node = base_station_set[dst]
        
        paths = path_controller.PathController.get_shortest_path(graph, source_node, target_node, 10)
        
        if len(paths) > 1:
            print(f'\niteration {it}\n')
            for path in paths:
                print(path)
                route_throughput = network_controller.NetworkController.get_route_net_throughput(graph, path[0])
                print(f'\n')
            a = input('')
        
        '''
        if len(paths) > 1:
            print(f'\n\nIteration: {it}')
            pprint(paths)
            a = input('') 
        '''
        
        
    
        '''

        widest_path, widest_path_cost = path_controller.PathController.get_widest_path(graph, source_node, target_node, 10)
        
        shortest_widest_path, shortest_widest_path_cost = path_controller.PathController.get_shortest_widest_path(graph, source_node, target_node, 10)
        
        if widest_path != shortest_widest_path:
            print(f'\nIteration: {it}')
            print(f'Widest and shortest-widest path are not the same')
            route_latency = network_controller.NetworkController.get_route_net_latency(graph, widest_path)
            print(f'\nWidest path - cost: {widest_path_cost} | latency ({route_latency})')
            print(f" -> ".join(widest_path))
            
            route_latency = network_controller.NetworkController.get_route_net_latency(graph, shortest_widest_path)
            print(f'\nShortest-widest path - cost: {shortest_widest_path_cost} | latency ({route_latency})')
            print(f" -> ".join(shortest_widest_path))
            a = input('')
        '''
        
        '''
        shortest_path, shortest_path_cost = path_controller.PathController.get_shortest_path(graph, source_node, target_node, 10)
        
        widest_shortest_path, widest_shortest_path_cost = path_controller.PathController.get_widest_shortest_path(graph, source_node, target_node, 10)
        
        if shortest_path != widest_shortest_path:
            print(f'\nIteration: {it}')
            print(f'Shortest and widest-shortest path are not the same')
            
            route_throughput = network_controller.NetworkController.get_route_throughut(graph, shortest_path)
            
            print(f'\nShortest path - cost: {shortest_path_cost} | throughput ({route_throughput})')
            print(" -> ".join(shortest_path))
            
            route_throughput = network_controller.NetworkController.get_route_throughut(graph, widest_shortest_path)
            print(f'\nWidest-shortest path - cost: {widest_shortest_path_cost} | throughput ({route_throughput})')
            print(" -> ".join(widest_shortest_path))
            
            a = input('')
        '''
    
    
    
    """
    
    source_node = base_station_set['17']
    target_node = base_station_set['18']
    
    # print(f'\n*** SHORTEST PATH ALGORITHM ***\n')
    # required_throughput = 20
    # path, cost = path_controller.PathController.get_shortest_path(graph, source_node, target_node, required_throughput)
    # widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    # print(f'route found with cost {widest_throughput} MBps ({cost} ms)')
    # print(" -> ".join(path))
    
    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path, required_throughput)
    
    # print(f'\n*** SHORTEST PATH ALGORITHM ***\n')
    # required_throughput = 36
    # path, cost = path_controller.PathController.get_shortest_path(graph, source_node, target_node, required_throughput)
    # widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    # print(f'route found with cost {widest_throughput} MBps ({cost} ms)')
    # print(" -> ".join(path))
    
    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path, required_throughput)
    
    # print(f'\n*** SHORTEST PATH ALGORITHM ***\n')
    # required_throughput = 55
    # path, cost = path_controller.PathController.get_shortest_path(graph, source_node, target_node, required_throughput)
    # widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    # print(f'route found with cost {widest_throughput} MBps ({cost} ms)')
    # print(" -> ".join(path))
    
    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path, required_throughput)

    # print(f'\n*** WIDEST SHORTEST PATH ALGORITHM ***\n')
    # required_throughput = 25
    # paths = path_controller.PathController.get_widest_shortest_path(graph, source_node, target_node, required_throughput)
    
    # for path in paths:
    #     widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path[0])
    #     print(f'\nroute found with cost {widest_throughput} MBps ({path[1]} ms)')
    #     print(" -> ".join(path[0]))
  
    
    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path[0], required_throughput)
    
    # print(f'\n*** WIDEST SHORTEST PATH ALGORITHM ***\n')
    
    # required_throughput = 55
    # paths = path_controller.PathController.get_widest_shortest_path(graph, source_node, target_node, required_throughput)
    
    # for path in paths:
    #     widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path[0])
    #     print(f'\nroute found with cost {widest_throughput} MBps ({path[1]} ms)')
    #     print(" -> ".join(path[0]))
    
    
    # print(f'________________________________________________________________')

    # print(f'\n*** WIDEST PATH ALGORITHM ***\n')
    
    # required_throughput = 20
    # path, cost = path_controller.PathController.get_widest_path(graph, source_node, target_node, required_throughput)
    # latency_cost = network_controller.NetworkController.get_route_net_latency(graph, path)
    # print(f'route found with cost {cost} MBps ({latency_cost} ms)')
    # print(" -> ".join(path))

    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path, required_throughput)
    
    # print(f'\n*** WIDEST PATH ALGORITHM ***\n')

    # required_throughput = 55
    # path, cost = path_controller.PathController.get_widest_path(graph, source_node, target_node, required_throughput)
    # latency_cost = network_controller.NetworkController.get_route_net_latency(graph, path)
    # print(f'route found with cost {cost} MBps ({latency_cost} ms)')
    # print(" -> ".join(path))
    
    
    
    print(f'\n*** SHORTEST WIDEST PATH ALGORITHM ***\n')
    
    required_throughput = 25
    paths = path_controller.PathController.get_shortest_widest_path(graph, source_node, target_node, required_throughput)
    # pprint(paths)
    for path in paths:
        latency_cost = network_controller.NetworkController.get_route_net_latency(graph, path[0])
        print(f'\nroute found with cost {path[1]} MBps ({latency_cost} ms)')
        print(" -> ".join(path[0]))
    
    network_controller.NetworkController.increase_bandwidth_reservation_test(graph, paths[0][0], required_throughput)
    
    # generate_networks.plot_graph(graph.graph)
    # a = input('')

    print(f'\n*** SHORTEST WIDEST PATH ALGORITHM ***\n')
    
    required_throughput = 55
    paths = path_controller.PathController.get_shortest_widest_path(graph, source_node, target_node, required_throughput)
    # pprint(paths)
    for path in paths:
        latency_cost = network_controller.NetworkController.get_route_net_latency(graph, path[0])
        print(f'\nroute found with cost {path[1]} MBps ({latency_cost} ms)')
        print(" -> ".join(path[0]))
    
    
    
    # print(f'________________________________________________________________')
    # print(f'\n*** FLATWISE ALGORITHM ***')
    
    # generate_networks.plot_graph(graph.graph)
    
    # latency_requirement = 6
    # required_throughput = 25
    # print(f'\nLATENCY REQUIREMENT: {latency_requirement} ms')
    
    # previous_nodes, shortest_path, = FLATWISE(graph, base_station_set, source_node, target_node, latency_requirement, required_throughput)
    # path, cost = calculate_shortest_path(previous_nodes, shortest_path, source_node, target_node)
    # widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    # print(f'route found with cost {widest_throughput} Mbps ({cost} ms)')
    # print(" -> ".join(path))
    
    # network_controller.NetworkController.increase_bandwidth_reservation_test(graph, path, required_throughput)
    
    # latency_requirement = 3
    # required_throughput = 50
    # print(f'\nLATENCY REQUIREMENT: {latency_requirement} ms')
    
    # previous_nodes, shortest_path, = FLATWISE(graph, base_station_set, source_node, target_node, latency_requirement, required_throughput)
    # path, cost = calculate_shortest_path(previous_nodes, shortest_path, source_node, target_node)
    # widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    # print(f'route found with cost {widest_throughput} Mbps ({cost} ms)')
    # print(" -> ".join(path))
    
    # routes = []
    # unique_routes = 0
    # for i in range(3, 11):
        
    #     latency_requirement = i
    #     print(f'\nLATENCY REQUIREMENT: {latency_requirement} ms')
    #     previous_nodes, shortest_path, = FLATWISE(graph, base_station_set, source_node, target_node, latency_requirement, required_throughput)
    #     path, cost = calculate_shortest_path(previous_nodes, shortest_path, source_node, target_node)
    #     widest_throughput = network_controller.NetworkController.get_route_widest_throughput(graph, path)
    #     print(f'route found with cost {widest_throughput} Mbps ({cost} ms)')
    #     print(" -> ".join(path))
    #     if path not in routes:
    #         routes.append(path)
            
        
    # print(f'\n***there are {len(routes)} unique routes')
    # a = input('')
    """
        
    # initial_distance = euclidean_distance(source_node, target_node)

    # for src, dst in pairwise(path):
    #     src_bs = base_station_set[src[2:]]
    #     current_distance = euclidean_distance(src_bs, target_node)
    #     current_percentage = (current_distance * 100) / initial_distance
    #     print(f'current node {src} is {current_percentage}% away from goal node {target_node.bs_name}')
     
    
    # print(" -> ".join(path))
    # print(f'cost: {cost}')
    
    # print(f'\nWIDEST PATH')
    # network_controller.NetworkController.get_route_net_throughput(graph, path)
    
    
    ###########################################################################

    ### SHORTEST AND WIDEST PATH TEST###

    print(f'\n################ START NODE ################\n')
    print(source_node.bs_name) 
    #pprint(graph.graph)
    #a = input('')
    dijkstra_controller.DijkstraController.get_shortest_path_all_paths(
        graph, source_node, base_station_set
    )

    dijkstra_controller.DijkstraController.get_E2E_shortest_path_all_paths(
        graph, source_node, base_station_set
    )

    dijkstra_controller.DijkstraController.get_E2E_throughput_widest_path_all_paths_without_restrictions(
        graph, source_node, base_station_set
    )
    """


    """ 
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
    """



