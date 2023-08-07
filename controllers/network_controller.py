import typing

if typing.TYPE_CHECKING:
    """ model modules"""
    from models.hmd import VrHMD
    from models.base_station import BaseStation 
    from models.graph import Graph


from controllers import path_controller
from models.bitrates import BitRateProfiles
from utils.network import generate_networks 

bitrate_profiles = BitRateProfiles()


""" other modules """
import sys
import json
import logging
from typing import Dict
from itertools import tee
import matplotlib.pyplot as plt
from pprint import pprint as pprint

#logging.basicConfig(level=logging.INFO)

'''
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s - %(message)s')
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
'''

MIN_VALUE = -10**9
MAX_VALUE = sys.maxsize
MIN_THROUGHPUT = 25
MAX_THROUGHPUT = 4153
MIN_LATENCY = 10
MAX_LATENCY = 56

MINIMUN_AVAILABLE_BANDWIDTH = 1024 #Mbps


class NetworkController:
    
    @staticmethod
    def __pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)

    @staticmethod
    def check_graph_bandwidth_increase_availability(graph: 'Graph', src: str, dst: str, required_bandwidth: float) -> bool:
        graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
        current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
        if current_available_bandwidth - required_bandwidth >= 0:
            return True
        return False
    
    @staticmethod
    def check_graph_bandwidth_decrease_availability(graph: 'Graph', src: str, dst: str, decreased_throughput: float) -> bool:
        graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
        current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
        if current_allocated_bandwidth - decreased_throughput >= 0:
            return True
        return False
    
    @staticmethod
    def check_graph_bandwidth_deallocation_availability(graph: 'Graph', src: str, dst: str, deallocated_throughput: float) -> bool:
        graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
        current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
        if current_allocated_bandwidth - deallocated_throughput >= 0:
            return True
        return False

    @staticmethod
    def check_graph_path_bandwidth_increase_availability(graph: 'Graph', route: list, required_bandwidth: float) -> bool:
        for src, dst in NetworkController.__pairwise(route):
            if not NetworkController.check_graph_bandwidth_increase_availability(graph, src, dst, required_bandwidth):
                return False
        return True
    
    def check_graph_path_bandwidth_decrease_availability(graph: 'Graph', route: list, decreased_throughput: float) -> bool:
        for src, dst in NetworkController.__pairwise(route):
            if not NetworkController.check_graph_bandwidth_decrease_availability(graph, src, dst, decreased_throughput):
                return False
        return True
    
    @staticmethod
    def check_graph_path_bandwidth_deallocation_availability(graph: 'Graph', route: list, deallocated_throughput: float) -> bool:
        for src, dst in NetworkController.__pairwise(route):
            if not NetworkController.check_graph_bandwidth_deallocation_availability(graph, src, dst, deallocated_throughput):
                return False
        return True
    
    @staticmethod
    def check_route_bandwidth_availability(graph: 'Graph', route: list, required_bandwidth: float) -> bool:
        for src, dst in NetworkController.__pairwise(route):
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
            if current_available_bandwidth - required_bandwidth < 0:
                return False
        return True
    
    
    @staticmethod
    def deallocate_bandwidth(graph: 'Graph', flow_set: dict, flow_id: int):         
        """deallocates the bandwidth of the route set, flow set and graph, simultaneously"""
        
        flow = flow_set[flow_id]
        flow_route = flow['route']
        
        flow_quota = flow['current_quota']
        flow_route_throughput = flow_quota['throughput']               
        
        if not flow_route:
            return 
        
        if len(flow_route) == 1:
            print(f'\n*** ERROR: THIS ROUTE IS ALREADY DEALLOCATED! ***')
            a = input('CRASHED IN DEALLOCATE_BANDWIDTH!')
        
        if NetworkController.check_graph_path_bandwidth_deallocation_availability(graph, flow_route, flow_route_throughput):
            for src, dst in NetworkController.__pairwise(flow_route):
                graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
                current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
                current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
                
                new_allocated_bandwidth = current_allocated_bandwidth - flow_route_throughput
                new_available_bandwidth = current_available_bandwidth + flow_route_throughput
                
                NetworkController.update_graph_pair_bandwidth(
                    graph, 
                    src, 
                    dst, 
                    new_allocated_bandwidth, 
                    new_available_bandwidth
                )
        else:
            print(f'\n*** ERROR: GRAPH WILL HAVE NEGATIVE RESOURCE ALLOCATION ***')
            print(f'TRYING TO DEALOCATE: {flow_route_throughput} Mbps FROM ROUTE:')    
            print(' -> '.join(flow_route))
            
            for src, dst in NetworkController.__pairwise(flow_route):
            
                graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
                current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
                current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
                
                new_allocated_bandwidth = current_allocated_bandwidth - flow_route_throughput
                new_available_bandwidth = current_available_bandwidth + flow_route_throughput
                
                
                #if new_allocated_bandwidth < 0 or new_available_bandwidth < 0:
                print(f'\ncrashed from {src} -> {dst}')
                print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                    
            
            a = input('CRASHED IN DEALLOCATE_BANDWIDTH!')
    
        flow_set[flow_id]['throughput'] = 0
        flow_set[flow_id]['route'] = [-1]
        
    
    @staticmethod
    def update_graph_pair_bandwidth(graph: 'Graph', src: str, dst: str, new_allocated_bandwidth: float, new_available_bandwidth: float):
 
        #updating the allocated and available banwidth from src -> dst
        graph.graph[src][dst]['allocated_bandwidth'] = new_allocated_bandwidth
        graph.graph[src][dst]['available_bandwidth'] = new_available_bandwidth
        
        #updating the allocated and available banwidth from dst -> src
        graph.graph[dst][src]['allocated_bandwidth'] = new_allocated_bandwidth
        graph.graph[dst][src]['available_bandwidth'] = new_available_bandwidth
        
    
    @staticmethod 
    def get_graph_pair_bandwidth(graph: 'Graph', src: str, dst: str):
        current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
        current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
        
        result = {
            "current_allocated_bandwidth": current_allocated_bandwidth,
            "current_available_bandwidth": current_available_bandwidth
        }
        
        return result
        
    
    @staticmethod
    def show_graph_pair_bandwidth_reservation(src: str, dst: str, current_allocated_bandwidth: float, current_available_bandwidth: float, new_allocated_bandwidth: float, new_available_bandwidth: float):
        
        logging.debug(f'\nfrom {src} -> {dst}')
        logging.debug(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
        logging.debug(f'previous available bandwidth: {current_available_bandwidth} Mbps')
        logging.debug(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
        logging.debug(f'new available bandwidth: {new_available_bandwidth} Mbps')

    
    
    @staticmethod
    def decrease_bandwidth_reservation(
        graph: 'Graph', flow_set: dict, flow_id: int
    ):
        
        flow = flow_set[flow_id]
        flow_route = flow['route']
        flow_quota = flow['current_quota']
        flow_quota_name = flow['current_quota_name']
        
        flow_throughput = flow_quota['throughput']
             
        previous_quota_name, previous_quota = bitrate_profiles.get_previous_bitrate_quota(flow_quota_name)             
        previous_flow_throughput = previous_quota['throughput']
        decreased_throughput = flow_throughput - previous_flow_throughput
        
        if flow_throughput - decreased_throughput != previous_flow_throughput:
            print(f'\n*** ERROR: FLOW THROUGHPUT != PREVIOUS THROUGHPUT ***')
            print(f'flow throughput: {flow_throughput} Mbps')
            print(f'previous throughput: {previous_flow_throughput} Mbps')
            print(f'decreased throughput: {decreased_throughput} Mbps')
            a = input('CRASHED')
        
        if NetworkController.check_graph_path_bandwidth_decrease_availability(graph, flow_route, decreased_throughput):
            #print(f'\nDecreasing {decreased_throughput} Mbps for flow {flow_id}:')
            #print(f'current flow throughput: {flow_throughput}')
            #print(" -> ".join(route))
            #print(f'\ndecreasing {decreased_throughput} from  each pair of nodes in the route...')
            
            for src, dst in NetworkController.__pairwise(flow_route):
        
                graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
                current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
                current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
            
                new_allocated_bandwidth = current_allocated_bandwidth - decreased_throughput
                new_available_bandwidth = current_available_bandwidth + decreased_throughput
                
                NetworkController.update_graph_pair_bandwidth(
                    graph, 
                    src, 
                    dst, 
                    new_allocated_bandwidth, 
                    new_available_bandwidth
                )
        
        
        else:
            print(f'\n*** ERROR: GRAPH WILL HAVE NEGATIVE RESOURCE AVAILABILITY ***')
            print(f'TRYING TO DEALOCATE: {decreased_throughput} Mbps FROM ROUTE:')    
            print(' -> '.join(flow_route))
            
            for src, dst in NetworkController.__pairwise(flow_route):
            
                graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
                current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
                current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
                
                new_allocated_bandwidth = current_allocated_bandwidth - decreased_throughput
                new_available_bandwidth = current_available_bandwidth + decreased_throughput
                
                
                #if new_allocated_bandwidth < 0 or new_available_bandwidth < 0:
                print(f'\ncrashed from {src} -> {dst}')
                print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                    
            
            a = input('CRASHED IN DRECRASE_BANDWIDTH!')
            
        
        flow_set[flow_id]['current_quota'] = previous_quota
        flow_set[flow_id]['current_quota_name'] = previous_quota_name
       

    
    
    @staticmethod
    def increase_bandwidth_reservation(
        graph: 'Graph', flow_set: dict, flow_id: int, new_route: list, required_quota: dict, required_quota_name: str
    ):
        #print(f'\nIncreasing BW reservation to {required_throughput} Mbps for route:')
        #print(" -> ".join(new_route))
        
        #print(f'\nincreasing each pair of nodes in the route...')
        current_quota = flow_set[flow_id]['current_quota']
        current_quota_name = flow_set[flow_id]['current_quota_name']
        
        current_route_bandwidth = current_quota['throughput']
        
        if not NetworkController.check_graph_path_bandwidth_increase_availability(graph, new_route, required_quota["throughput"]):
            print(f'\n*** Widest Path found a route but there is no more available resources for route:***')
            print(' -> '.join(new_route))
            print(f'current route bandwidth: {current_route_bandwidth} Mbps')
            print(f'requested increase: {required_quota["throughput"]} Mbps')
            a = input('')
        
        for src, dst in NetworkController.__pairwise(new_route):
            
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            
            current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
        
            new_allocated_bandwidth = current_allocated_bandwidth + required_quota["throughput"]
            new_available_bandwidth = current_available_bandwidth - required_quota["throughput"]
            
            NetworkController.show_graph_pair_bandwidth_reservation(
                src, 
                dst, 
                current_allocated_bandwidth, 
                current_available_bandwidth, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
            if new_available_bandwidth < 0 or new_allocated_bandwidth < 0:
                a = input('\n***CRASHED in increase_bandwidth_reservation!***')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
        
        flow_set[flow_id]['current_quota'] = required_quota
        flow_set[flow_id]['current_quota_name'] = required_quota_name
        
        flow_set[flow_id]['route'] = new_route
        
    @staticmethod
    def increase_bandwidth_reservation_test(
        graph: 'Graph', route, required_throughput: float
    ):
        
        for src, dst in NetworkController.__pairwise(route):
            
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            
            current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
        
            new_allocated_bandwidth = current_allocated_bandwidth + required_throughput
            new_available_bandwidth = current_available_bandwidth - required_throughput
            
            NetworkController.show_graph_pair_bandwidth_reservation(
                src, 
                dst, 
                current_allocated_bandwidth, 
                current_available_bandwidth, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
            if new_available_bandwidth < 0 or new_allocated_bandwidth < 0:
                a = input('\n***CRASHED in increase_bandwidth_reservation!***')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
    
    staticmethod    
    def congested_route(graph: 'Graph', src: str, dst: str) -> bool:
        graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
        current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
        if current_available_bandwidth < MINIMUN_AVAILABLE_BANDWIDTH:
            return True
        return False
        
    @staticmethod
    def get_congested_edges_in_route(graph: 'Graph', route: list) -> list:
        congested_edges = []
        for src, dst in NetworkController.__pairwise(route):
            if NetworkController.congested_route(graph, src, dst):
                congested_edges.append((src, dst))
        return congested_edges
    
    @staticmethod
    def congestion_management(
        graph: 'Graph', flow_set: dict, prioritized_served_flows: list, non_prioritized_served_flows: list, congestion_iterations: int
    ) -> None:
        # if congestion_iterations == 100:
        #     print(non_prioritized_served_flows)
        #     print(prioritized_served_flows)
            # a = input('')
        
        reachable_flows = False
        congested_edges_found = False
        
        for non_prioritized_flow in non_prioritized_served_flows.copy():
            served_flow = flow_set[non_prioritized_flow]
            served_flow_route = served_flow['route']
            served_flow_quota = served_flow['current_quota']
            served_flow_quota_name = served_flow['current_quota_name']
            served_flow_throughput = served_flow_quota['throughput']
            
            congested_edges = NetworkController.get_congested_edges_in_route(graph, served_flow_route)
            
            if congested_edges:            
                if served_flow_throughput > MIN_THROUGHPUT:
                    NetworkController.decrease_bandwidth_reservation(
                        graph, flow_set, non_prioritized_flow
                    )
                    reachable_flows = True
                else:
                    non_prioritized_served_flows.remove(non_prioritized_flow)
                    
        if not reachable_flows:
            if congestion_iterations > 50:
                print(f'BEFORE: size of prioritized flows: {len(prioritized_served_flows)}')
                print(f' size of non prioritized flows: {len(non_prioritized_served_flows)}')
                a = input('checking on prioritized flows...')
            for prioritized_flow in prioritized_served_flows.copy():
                served_flow = flow_set[prioritized_flow]
                served_flow_route = served_flow['route']
                served_flow_quota = served_flow['current_quota']
                served_flow_quota_name = served_flow['current_quota_name']
                served_flow_throughput = served_flow_quota['throughput']
                
                congested_edges = NetworkController.get_congested_edges_in_route(graph, served_flow_route)
                
                if congested_edges:            
                    if served_flow_throughput > MIN_THROUGHPUT:
                        NetworkController.decrease_bandwidth_reservation(
                            graph, flow_set, prioritized_flow
                        )
                    else:
                        prioritized_served_flows.remove(prioritized_flow)
                        
                    congested_edges_found = True
            
            if not congested_edges_found:
                for prioritized_flow in prioritized_served_flows.copy():
                    served_flow = flow_set[prioritized_flow]
                    served_flow_route = served_flow['route']
                    served_flow_quota = served_flow['current_quota']
                    served_flow_quota_name = served_flow['current_quota_name']
                    served_flow_throughput = served_flow_quota['throughput']
                    
                    if served_flow_throughput > MIN_THROUGHPUT:
                        NetworkController.decrease_bandwidth_reservation(
                            graph, flow_set, prioritized_flow
                        )
                    else:
                        # print(served_flow_quota)
                        # print(f'served flow throughput: {served_flow_throughput} Mbps')
                        # print(f'min throughput: {MIN_THROUGHPUT} Mbps')
                        # print(served_flow_route)
                        # a = input('')
                        prioritized_served_flows.remove(prioritized_flow)
                    
            if congestion_iterations > 50:
                print(f'AFTER: size of prioritized flows: {len(prioritized_served_flows)}')
                print(f' size of non prioritized flows: {len(non_prioritized_served_flows)}')
                a = input('')
                        
        if not reachable_flows:
            print(f'\nCongestion iteration: {congestion_iterations} -> NON-PRIORITIZED FLOWS')
        else:
            print(f'\nCongestion iteration: {congestion_iterations} -> PRIORITIZED FLOWS')
        
    @staticmethod
    def get_route_net_latency(graph: 'Graph', route: list) -> float:
        net_latency = 0
        for src, dst in NetworkController.__pairwise(route):
            net_latency += graph.graph[src][dst]['network_latency']
             
        return round(net_latency, 2)
    
    @staticmethod
    def get_route_net_throughput(graph: 'Graph', route: list) -> float:
        net_throughput = 0
        for src, dst in NetworkController.__pairwise(route):
            if graph.graph[src][dst]['network_throughput'] > net_throughput:
                net_throughput += graph.graph[src][dst]['network_throughput']
        return net_throughput
    
    @staticmethod
    def get_route_widest_throughput(graph: 'Graph', route: list) -> float:
        widest_throughput = MAX_VALUE
        for src, dst in NetworkController.__pairwise(route):
            if graph.graph[src][dst]['available_bandwidth'] < widest_throughput:
                widest_throughput = graph.graph[src][dst]['available_bandwidth']
            
        return widest_throughput    
    
        
    @staticmethod
    def allocate_bandwidth(
        base_station_set: Dict[str, 'BaseStation'], graph: 'Graph', routing_algorithm: str, source_node: 'BaseStation', target_node: 'BaseStation', flow_set: dict, prioritized_served_flows: list, non_prioritized_served_flows: list, flow_id: int, impaired_services: dict
    ):

        flow = flow_set[flow_id]
        
        required_quota = flow['next_quota']
        required_quota_copy = required_quota
        required_quota_name = flow['next_quota_name']
        # print(f'\nrequired quota')
        # print(required_quota)
        required_latency = required_quota['latency']
        required_throughput = required_quota['throughput']
        
        
        new_route = None
        
        
        if routing_algorithm == 'wsp':
            new_route, route_max_latency = path_controller.PathController.get_widest_shortest_path(
                graph, source_node, target_node, required_throughput
            )
            
        elif routing_algorithm == 'swp':
            new_route, route_max_throughput = path_controller.PathController.get_shortest_widest_path(
                graph, source_node, target_node, required_throughput
            )
            if new_route:
                route_max_latency = NetworkController.get_route_net_latency(graph, new_route)
        
        elif routing_algorithm == 'flatwise':
            new_route, route_max_latency = path_controller.PathController.get_flatwise_path(
                base_station_set, graph, source_node, target_node, required_latency, required_throughput
            )
        
        congestion_iterations = 1
        
        while not new_route or route_max_latency > required_latency:
            # print(f'\n*** no routes to fulfill latency or throughput: flow id: {flow_id} ***')
            # print(f'*** latency found: {route_max_latency} | required latency: {required_latency} ms ***')
            # print(f'*** throughput found: {route_max_throughput} | required throughput: {required_throughput} Mbps ***')
            
            # print(f'*** recalculating a new route ***')
            
            # a = input('type to continue...')
                
            # previous_throughput = required_throughput
            impaired_services['services'] += 1
            
            previous_quota_name, previous_quota = bitrate_profiles.get_previous_bitrate_quota(required_quota_name)
            
            required_quota = previous_quota
            required_quota_name = previous_quota_name
            required_throughput = previous_quota['throughput']
            required_latency = previous_quota['latency']
                
            NetworkController.congestion_management(
                graph, flow_set, prioritized_served_flows, non_prioritized_served_flows, congestion_iterations
            )
            
            congestion_iterations += 1
            
            if congestion_iterations == 50:
                print(source_node.bs_name)
                print(target_node.bs_name)
                print(required_quota_copy)
                print(required_quota)
                print(route_max_latency)
                print(f' -> '.join(new_route))
                a = input('')
            
            if routing_algorithm == 'wsp':
                new_route, route_max_latency = path_controller.PathController.get_widest_shortest_path(
                    graph, source_node, target_node, required_throughput
                )
                
            elif routing_algorithm == 'swp':
                new_route, route_max_throughput = path_controller.PathController.get_shortest_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                if new_route:
                    route_max_latency = NetworkController.get_route_net_latency(graph, new_route)
            
            elif routing_algorithm == 'flatwise':
                new_route, route_max_latency = path_controller.PathController.get_flatwise_path(
                    base_station_set, graph, source_node, target_node, required_latency, required_throughput
                )
            
            
            # new_route, route_max_throughput = path_controller.DijkstraController.get_widest_path(
            #     graph, source_node, target_node, required_throughput
            # )
        
        # a = input('type to increase bw reservation..')
        if required_latency < route_max_latency:
            print(f'\n*** ERROR: REQUIRED LATENCY < ROUTE MAX LATENCY ***')
            print(required_quota_copy)
            print(required_quota)
            print(f'route max latency: {route_max_latency} ms')
            a = input('')
        NetworkController.increase_bandwidth_reservation(graph, flow_set, flow_id, new_route, required_quota, required_quota_name)

        # return required_throughput
        
    
    
    @staticmethod
    def generate_network_plot(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.title("Network Graph")
        plt.xlabel("X")
        plt.ylabel("Y")
        
        for base_station in base_station_set.values():
            bs_x_position = base_station.position[0]
            bs_y_position = base_station.position[1]
            circle = plt.Circle((bs_x_position, bs_y_position), base_station.signal_range, color='blue', alpha=0.1)
            plt.gca().add_patch(circle)
            plt.scatter(bs_x_position, bs_y_position, color='blue', marker='o')
            plt.annotate('BS{}'.format(base_station.id), xy=(bs_x_position, bs_y_position), ha='center', va='bottom', color='black')
            
        for hmd_id, hmd in hmds_set.items():
            hmd_x_position = hmd.position[0]
            hmd_y_position = hmd.position[1]
            circle = plt.Circle((hmd_x_position, hmd_y_position), hmd.signal_range, color='red', alpha=0.1)
            #print(circle)
            plt.gca().add_patch(circle)
            plt.scatter(hmd_x_position, hmd_y_position, color='red', marker='x')
            plt.annotate('HMD{}'.format(hmd.id), xy=(hmd_x_position, hmd_y_position), ha='center', va='bottom', color='black')
        
        plt.pause(5)
        plt.clf()
        
    @staticmethod
    def print_network(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        plt.figure(figsize=(12, 12))
        while True:
            NetworkController.generate_network_plot(base_station_set, hmds_set)

    @staticmethod
    def reduce_edge_net_latencies(file_dir, json_file):
        # Load the JSON data from the file
        
        with open("{}{}".format(file_dir, json_file)) as f:
            data = json.load(f)
        
        # Reduce 0.3 from each value in the "edge_net_latencies" list
        for bs_data in data["base_station_set"].values():
            edge_net_latencies = bs_data["edge_net_latencies"]
            bs_data["edge_net_latencies"] = [latency - 0.3 for latency in edge_net_latencies]
            bs_data["edge_net_latencies"] = [round(latency, 2)  for latency in edge_net_latencies]
        
        # Write the updated JSON data back to the file
        with open("{}{}".format(file_dir, json_file), "w") as f:
            json.dump(data, f, indent=2)