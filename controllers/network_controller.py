import typing

if typing.TYPE_CHECKING:
    """ model modules"""
    from models.hmd import VrHMD
    from models.base_station import BaseStation 
    from models.graph import Graph


from controllers import dijkstra_controller
from models.bitrates import BitRateProfiles
from utils.network import generate_networks 

bitrate_profiles = BitRateProfiles()


""" other modules """
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
MIN_THROUGHPUT = 10
MAX_THROUGHPUT = 250

MINIMUN_AVAILABLE_BANDWIDTH = 50 #Mbps


class NetworkController:
    
    @staticmethod
    def __pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)

    @staticmethod
    def update_graph_pair_bandwidth(graph: 'Graph', src: str, dst: str, new_allocated_bandwidth: float, new_available_bandwidth: float):
        #if LOGS:
        #    print(f'\n*** updating graph')
        
        if new_available_bandwidth < 0:
            a = input('AVAILABLE CANNOT BE NEGATIVE!')
        
        if new_allocated_bandwidth < 0:
            a = input('ALLOCATED CANNOT BE NEGATIVE!')    
        
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
    def deallocate_bandwidth(graph: 'Graph', route_set: dict, flow_set: dict, route_id: str, flow_id: int):
                
        current_route = route_set[route_id]['route']
        current_route_bandwidth = route_set[route_id]['total_route_bandwidth']
            
        logging.debug(f'\nDEALLOCATING CURRENT ROUTE')
        logging.debug(" -> ".join(current_route))
        logging.debug(f'\ndealocating bandwidth for each pair of the route\n')        
    
        for src, dst in NetworkController.__pairwise(current_route):
            
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
            
            new_allocated_bandwidth = current_allocated_bandwidth - current_route_bandwidth
            new_available_bandwidth = current_available_bandwidth + current_route_bandwidth
            
            '''
            NetworkController.show_graph_pair_bandwidth_reservation(
                src, 
                dst, 
                current_allocated_bandwidth, 
                current_available_bandwidth, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            '''
            
            if new_allocated_bandwidth < 0 or new_available_bandwidth < 0:
                #print(f'printing graph...')    
                #generate_networks.plot_graph(graph.graph)
                print(f'previous route bandwidth: {current_route_bandwidth}')    
                a = (f'CRASHED IN DEALLOCATE_BANDWIDTH!')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
        logging.debug(f'\n***updating route_set')
        logging.debug(f'previous route bandwidth: {current_route_bandwidth}')            

        route_set[route_id]['total_route_bandwidth'] = 0
        route_set[route_id]['route'] = []
        
        logging.debug(f'\nsucessfully deallocated bandwidth: {current_route_bandwidth} Mbps')
        logging.debug(f'\nnew route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
    
        logging.debug(f'\n*** updating flow_set')
        flow_set[flow_id]['throughput'] = 0
    
    @staticmethod
    def decrease_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_set: dict, route: list, route_id: str, flow_id: int, flow_throughput: float
    ):
        
        if flow_throughput == MIN_THROUGHPUT:
            logging.debug(f'\nFlow {flow_id} already reached the minimum resolution!')
            return
            
        
        previous_flow_throughput = bitrate_profiles.get_previous_throughput_profile(flow_throughput) 
        decreased_throughput = flow_throughput - previous_flow_throughput
        
        logging.debug(f'\nDecreasing {decreased_throughput} Mbps for route:')
        logging.debug(" -> ".join(route))
        logging.debug(f'\ndecreasing {decreased_throughput} from  each pair of nodes in the route...')
        
        for src, dst in NetworkController.__pairwise(route):
    
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
        
            new_allocated_bandwidth = current_allocated_bandwidth - decreased_throughput
            new_available_bandwidth = current_available_bandwidth +  decreased_throughput
            
            NetworkController.show_graph_pair_bandwidth_reservation(
                src, 
                dst, 
                current_allocated_bandwidth, 
                current_available_bandwidth, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
            if new_available_bandwidth < 0 or new_allocated_bandwidth < 0:
                logging.debug(f'current flow throughput: {flow_throughput}')
                logging.debug(f'previous flow throughput: {previous_flow_throughput}')
                a = ('\n***CRASHED in decrease_bandwidth_reservation!***')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
          

        logging.debug(f'\n *** updating route_set')
        logging.debug(f'\nprevious route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        route_set[route_id]['total_route_bandwidth'] = previous_flow_throughput
        
        logging.debug(f'\nnew route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        logging.debug(f'\n*** updating flow_set')
        flow_set[flow_id]['throughput'] = previous_flow_throughput
            
        #a = input('\ntype to continue...\n')

    
    
    @staticmethod
    def increase_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_set: dict, flow_id: int, new_route: list, route_id: str, required_throughput: float
    ):
        logging.debug(f'\nIncreasing BW reservation to {required_throughput} Mbps for route:')
        logging.debug(" -> ".join(new_route))
        logging.debug(f'\nincreasing each pair of nodes in the route...')
        
        for src, dst in NetworkController.__pairwise(new_route):
            
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
                
        
        logging.debug(f'\n *** updating route_set')
        logging.debug(f'\nprevious route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        route_set[route_id]['total_route_bandwidth'] = required_throughput
        route_set[route_id]['route'] = new_route
        
        logging.debug(f'new route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')

        logging.debug(f'\n***updating flow_set')
        flow_set[flow_id]['throughput'] = required_throughput

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
    def congestion_management(graph: 'Graph', route_set: dict, flow_set: dict, served_flows: list):
        
        print(f'\n***Network bandwidth congestion management***')
        for flow_id in served_flows:
            flow = flow_set[flow_id]
            flow_throughput = flow['throughput']
            src_id = flow['client']
            route_id = str(src_id)
            route = route_set[route_id]['route']
            congested_edges = NetworkController.get_congested_edges_in_route(graph, route)
            if congested_edges:
                if flow_throughput > MIN_THROUGHPUT:
                    NetworkController.decrease_bandwidth_reservation(
                        graph, route_set, flow_set, route, route_id, flow_id, flow_throughput
                    )
                else:
                    print(f'\nFlow {flow_id} already reached the minimum resolution!')
                    print(f'\nRemoving flow {flow_id} from served flows')
                    served_flows.remove(flow_id)
                    #a = input('type to continue...')
            
            print(f'finished congestion processing for flow {flow_id}, type to continue...')
                    
            

    staticmethod
    def initialize_route_set(hmds_set: dict[str, 'VrHMD'], route_set: dict):
        for hmd_id, hmd in hmds_set.items():    
            route_set[hmd_id] = {
                'route': [],
                'total_route_bandwidth': 0
            }
            
        
    @staticmethod
    def allocate_bandwidth(
        graph: 'Graph', route_set: dict, route_id: str, source_node: 'BaseStation', target_node: 'BaseStation', flow_set: dict, served_flows: list, flow_id: int, required_throughput: float, already_deallocated: bool, prioritized_flow: bool
    ):
    
        new_route = None
        
        if not route_set[route_id]['route']:
            logging.debug(f'\n*** NEW ROUTE ***')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            while route_max_throughput == MIN_VALUE:
                logging.debug(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                logging.debug(f'*** recalculating a new route ***')
                    
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                    
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    logging.debug(f'\nFLOW PRIORITIZATION: {prioritized_flow}\n')
                    logging.debug(f'printing graph...')    
                    generate_networks.plot_graph(graph.graph)
                    if not served_flows:
                        a = input('no served flows were processed!')
                    
                    else:
                        while route_max_throughput == MIN_VALUE:
                            NetworkController.congestion_management(graph, route_set, flow_set, served_flows)
                            
                            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                                graph, source_node, target_node, required_throughput
                            )
                    #a = input('\nno more resources available 1!\n')
                    
            
            route_set[route_id]['route'] = new_route
            route_set[route_id]['total_route_bandwidth'] = 0
            
            NetworkController.increase_bandwidth_reservation(graph, route_set, flow_set, flow_id, new_route, route_id, required_throughput)
            #a = input('')
            
        else:
            
            logging.debug(f'\n*** ROUTE ALREADY EXISTS! ***')
            
            route = route_set[route_id]['route']
            logging.debug(" -> ".join(route))
            
            NetworkController.deallocate_bandwidth(
                graph, route_set, flow_set, route_id, flow_id
            )
            
            logging.debug(f'\nRECALCULATING A NEW ROUTE')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            while route_max_throughput == MIN_VALUE:
                logging.debug(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                logging.debug(f'*** recalculating a new route ***')
                    
                
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    logging.debug(f'\nFLOW PRIORITIZATION: {prioritized_flow}\n')
                    logging.debug(f'printing graph...')    
                    generate_networks.plot_graph(graph.graph)
                    
                    if not served_flows:
                        a = input(f'\nno served flows were processed!')
                    
                    else:
                        while route_max_throughput == MIN_VALUE:
                            NetworkController.congestion_management(graph, route_set, flow_set, served_flows)
                            
                            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                                graph, source_node, target_node, required_throughput
                            )
                    #a = input('\nno more resources available!\n')
            
            NetworkController.increase_bandwidth_reservation(graph, route_set, flow_set, flow_id, new_route, route_id, required_throughput)
        

        return required_throughput
        
    
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