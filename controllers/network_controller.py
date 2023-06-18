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
import time
import numpy as random
from typing import Dict
from itertools import tee
import matplotlib.pyplot as plt
from pprint import pprint as pprint

MIN_VALUE = -10**9
MIN_THROUGHPUT = 10
MAX_THROUGHPUT = 250
LOGS = True
F = 0

class NetworkController:
    
    @staticmethod
    def __pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)

    @staticmethod
    def update_graph_pair_bandwidth(graph: 'Graph', src: str, dst: str, new_allocated_bandwidth: float, new_available_bandwidth: float):
        print(f'\n*** updating graph')
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
        
        if LOGS:
            print(f'\nfrom {src} -> {dst}')
            print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
            print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
            print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
            print(f'new available bandwidth: {new_available_bandwidth} Mbps')

    
    @staticmethod
    def deallocate_bandwidth(graph: 'Graph', route_set: dict, flow_set: dict, route_id: str, flow_id: int):
                
        current_route = route_set[route_id]['route']
        current_route_bandwidth = route_set[route_id]['total_route_bandwidth']
            
        if LOGS:
            print(f'\nDEALLOCATING CURRENT ROUTE')
            print(" -> ".join(current_route))
            print(f'\ndealocating bandwidth for each pair of the route\n')        
        
        for src, dst in NetworkController.__pairwise(current_route):
            
            graph_bandwidth = NetworkController.get_graph_pair_bandwidth(graph, src, dst)
            current_allocated_bandwidth = graph_bandwidth['current_allocated_bandwidth']
            current_available_bandwidth = graph_bandwidth['current_available_bandwidth']
            
            new_allocated_bandwidth = current_allocated_bandwidth - current_route_bandwidth
            new_available_bandwidth = current_available_bandwidth + current_route_bandwidth
            
            NetworkController.show_graph_pair_bandwidth_reservation(
                src, 
                dst, 
                current_allocated_bandwidth, 
                current_available_bandwidth, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
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
            
                
            
        if LOGS:
            print(f'\n*** updating route_set')
            print(f'previous route bandwidth: {current_route_bandwidth}')            

        route_set[route_id]['total_route_bandwidth'] = 0
        
        if LOGS:
            print(f'\nsucessfully deallocated bandwidth: {current_route_bandwidth} Mbps')
            print(f'\nnew route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        if LOGS:
            print(f'\n*** updating flow_set')
            flow_set[flow_id]['throughput'] = 0
            
        #a = input('\ntype to continue...\n')
    
    @staticmethod
    def decrease_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_set: dict, served_flows: list, served_flow_id: int, route: list, route_id: str, flow_throughput: float
    ):
        
        previous_flow_throughput = bitrate_profiles.get_previous_throughput_profile(flow_throughput)
            
        if previous_flow_throughput is None:
            if LOGS:
                print(f'\n*** Could not decrease the resolution for served flow {served_flow_id} ***')
                print(f'*** removing {served_flow_id} from flow_set ***')
                served_flows.remove(served_flow_id)
                #print(f'Keep using the lowest throughput profile: {flow_throughput}')
            return 
        
        decreased_throughput = flow_throughput - previous_flow_throughput
        
        if LOGS:
            print(f'\nDecreasing {decreased_throughput} Mbps for route:')
            print(" -> ".join(route))
            print(f'\ndecreasing {decreased_throughput} from  each pair of nodes in the route...')
        
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
                #print(f'printing graph...')    
                #generate_networks.plot_graph(graph.graph)
                print(f'current flow throughput: {flow_throughput}')
                print(f'previous flow throughput: {previous_flow_throughput}')
                a = ('\n***CRASHED in decrease_bandwidth_reservation!***')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
          
    
            
        #source_node_id = route[0]

        if LOGS:
            print(f'\n *** updating route_set')
            #print(f'\nsource node: {source_node_id}')
            print(f'\nprevious route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        route_set[route_id]['total_route_bandwidth'] = previous_flow_throughput
        
        if LOGS:
            print(f'\nnew route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        if LOGS:
            print(f'\n*** updating flow_set')
            flow_set[served_flow_id]['throughput'] = previous_flow_throughput
            
        #a = input('\ntype to continue...\n')

    
    
    @staticmethod
    def increase_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_set: dict, flow_id: int, new_route: list, route_id: str, required_throughput: float
    ):
        if LOGS:
            print(f'\nIncreasing BW reservation to {required_throughput} Mbps for route:')
            print(" -> ".join(new_route))
            print(f'\nincreasing each pair of nodes in the route...')
        
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
                #print(f'printing graph...')    
                #generate_networks.plot_graph(graph.graph)
                a = input('\n***CRASHED in increase_bandwidth_reservation!***')
            
            NetworkController.update_graph_pair_bandwidth(
                graph, 
                src, 
                dst, 
                new_allocated_bandwidth, 
                new_available_bandwidth
            )
            
    
                
        #src_id = new_route[0]
        
        if LOGS:   
            #pass
            print(f'\n *** updating route_set')
            print(f'\nprevious route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')
        
        route_set[route_id]['total_route_bandwidth'] = required_throughput
        
        if LOGS:
            #pass
            print(f'new route bandwidth: {route_set[route_id]["total_route_bandwidth"]} Mbps')

        print(f'\n***updating flow_set')
        flow_set[flow_id]['throughput'] = required_throughput

        #a = input('\ntype to continue...\n')
    
    
    
    @staticmethod
    def check_served_flows(served_flows, route_set):
        print(f'\n*** checking served flows! ***\n')
        for flow_id in served_flows:
            g = False
            for bs, values in route_set.items():
                if flow_id in values.keys():
                    print(f'current served flow {flow_id} is deployed on: {bs}')
                    g = True
                    break
                    #print(f'route: {values[served_flow]["route"]}')
                    #print(f'total route bandwidth: {values[served_flow]["total_route_bandwidth"]} Mbps')
                    #a = input('')
            if not g:
                print(f'\n***current served flow {flow_id} not found in route_set***\n')
        print(f'\n')
                
    @staticmethod
    def check_served_flow(served_flows, route_set, flow_id):
        #print(f'\nchecking if {flow_id} is in route_set\n')
        for bs, values in route_set.items():
            if flow_id in values.keys():
                print(f'\ncurrent served flow {flow_id} is deployed on: {bs}\n')
                return True
                
        print(f'\n***current served flow {flow_id} NOT found in route_set***\n')
        return False
    
    @staticmethod
    def decrease_all_flow_resolutions(graph: 'Graph', hmds_set: 'VrHMD', route_set: dict, flow_set: dict, served_flows: list):
        #global LOGS 
        #LOGS = True
        #TODO: instead of decreasing all flow resolutions, we must look for all routes passing through the congested node and decrease the bandwidth of all routes passing through that node untill it satisfies at least one quota before the current quota.
        #TODO: after shifting all flow resolutions, we have to consider the current allocated throughput after the first iteration of this function. Consider also dealocating the route...
        
        print(f'\n*** DECREASING ALL FLOW RESOLUTIONS ***')
        #print(f'\nprinting the plot\n')
        #generate_networks.plot_graph(graph.graph)
        
        if LOGS:
            print(f'served flows: {served_flows}')
            if not served_flows:
                print(f'\nserved flow is empty!')
                generate_networks.plot_graph(graph.graph)
                a = input('type to continue')
        
        for served_flow in served_flows.copy():
            if LOGS:
                print(f'\n*************************************************************')
                print(f'\n*** served flow: {served_flow} ***')
            
            # HERE WE HAVE TO GET THE SRC AND DST BST AND NOT THE IDS IN THE FLOW...
            flow = flow_set[served_flow]
            src_id = flow['client']
            route_id = str(src_id)
                
            current_route = route_set[route_id]['route']
            flow_throughput = flow_set[served_flow]['throughput']
            
            NetworkController.decrease_bandwidth_reservation(
                graph, route_set, flow_set, served_flows, served_flow, current_route, route_id, flow_throughput
            )
                
        if LOGS:
            print(f'\n*** FINISH DECREASING ALL FLOW RESOLUTIONS ***')
            

    staticmethod
    def initialize_route_set(hmds_set: dict[str, 'VrHMD'], route_set: dict):
        for hmd_id, hmd in hmds_set.items():    
            route_set[hmd_id] = {
                'route': [],
                'total_route_bandwidth': 0
            }
            
        
    @staticmethod
    def allocate_bandwidth(
        graph: 'Graph', hmds_set: Dict[str, 'VrHMD'], route_set: dict, route_id: str, source_node: 'BaseStation', target_node: 'BaseStation', flow_set: dict, served_flows: list, flow_id: int, required_throughput: float
    ):
    
        #src_id = source_node.bs_name
        new_route = None
        global F
        if F > len(hmds_set):
            print(len(hmds_set))
            print(F)
            a = input('CRASHED BECAUSE THIS IF IS NOT WORKING!')
            
        
        if not route_set[route_id]['route']:
            F+=1
            if LOGS:
                print(f'\n*** NEW ROUTE ***')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            it = 0
            '''
            while route_max_throughput == MIN_VALUE:
                if LOGS:
                    print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                    print(f'*** recalculating a new route ***')
                
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                #print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    it += 1
                    #a = input('\nno more resources available!\n')
                    if LOGS:
                        print(f'\nUsing the lowest throughput profile: {required_throughput}')
                    #required_throughput = previous_throughput
                    NetworkController.decrease_all_flow_resolutions(graph, hmds_set, route_set, flow_set, served_flows)
                    if it % 10 == 0:
                        print(f'\n*** still processing FLOW ID {flow_id} at ITERATION {it} ***\n')
                        print(f'\nprinting the plot\n')
                        generate_networks.plot_graph(graph.graph)
                        print(f'route_max_throughput: {route_max_throughput}')
                        print(f'\ntrying a route from {source_node.bs_name} -> {target_node.bs_name}\n')
                        a = input('type to continue')
            '''
            
            route_set[route_id]['route'] = new_route
            route_set[route_id]['total_route_bandwidth'] = 0
            
            '''
            if src_id not in route_set.keys():
                route_set[src_id] = {
                    flow_id: {
                        'route': new_route,
                        'total_route_bandwidth': 0
                    }
                }
            
            else:
                route_set[src_id][flow_id] = {
                    'route': new_route,
                    'total_route_bandwidth': 0
                }
            '''
            
            NetworkController.increase_bandwidth_reservation(graph, route_set, flow_set, flow_id, new_route, route_id, required_throughput)
            #a = input('')
            
        else:
            
            if LOGS:
                print(f'\n*** ROUTE ALREADY EXISTS! ***')
            
            NetworkController.deallocate_bandwidth(
                graph, route_set, flow_set, route_id, flow_id
            )
            
            if LOGS:
                print(f'\nRECALCULATING A NEW ROUTE')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            it = 0            
            '''
            while route_max_throughput == MIN_VALUE:
                if LOGS:    
                    print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                    print(f'*** recalculating a new route ***')
                
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                #print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    it +=1
                    #a = input('\nno more resources available!\n')
                    if LOGS:
                        print(f'\nUsing the lowest throughput profile: {required_throughput}')
                    
                    NetworkController.decrease_all_flow_resolutions(graph, hmds_set, route_set, flow_set, served_flows)
                    
                    if it % 10 == 0:
                        print(f'\n*** still processing FLOW ID {flow_id} at ITERATION {it} ***\n')
                        print(f'\nprinting the plot\n')
                        generate_networks.plot_graph(graph.graph)
                        print(f'route_max_throughput: {route_max_throughput}')
                        print(f'\ntrying a route from {source_node.bs_name} -> {target_node.bs_name}\n')
                        a = input('type to continue')
            '''
            route_set[route_id]['route'] = new_route
            
            NetworkController.increase_bandwidth_reservation(graph, route_set, flow_set, flow_id, new_route, route_id, required_throughput)
        

        return required_throughput
        
        
        
        
        
        
        
    
        
    
    @staticmethod
    def reset_route(route_set: dict, hmd: 'VrHMD'):
        src_id = hmd.current_base_station
        del route_set[src_id]
    
    @staticmethod
    def check_banwidth_allocation(route_set: dict, hmd: 'VrHMD'):
        ''' calculate a new network throughput based on current network conditions '''
        
        '''
        1. delete current allocated route
        2. recalculate the route and pick up the maximum minumum throughput from widest path
        3. allocated the new route
        '''
        NetworkController.reset_route(route_set, hmd)
        
        
    
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
        '''
        '''
        
        plt.pause(0.01)
        plt.clf()
        
    @staticmethod
    def print_network(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        plt.figure(figsize=(12, 12))
        while True:
            NetworkController.generate_network_plot(base_station_set, hmds_set)