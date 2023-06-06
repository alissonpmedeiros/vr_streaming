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
import numpy as random
from typing import Dict
from itertools import tee
import matplotlib.pyplot as plt
from pprint import pprint as pprint

MIN_VALUE = -10**9
MAX_THROUGHPUT = 250

class NetworkController:
    
    @staticmethod
    def __pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)

    @staticmethod
    def generate_flow_order(vr_hmds: Dict[str, 'VrHMD']) -> list:
        hmd_keys = list(vr_hmds.keys())
        random.shuffle(hmd_keys)
        return hmd_keys
    
    @staticmethod
    def deallocate_bandwidth(graph: 'Graph', route_set: dict, source_id: str):
                
        path = route_set[source_id]['route']
        current_route_bandwidth = route_set[source_id]['total_route_bandwidth']
        
        for src, dst in NetworkController.__pairwise(path):
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
            
            updated_allocation = round(current_allocated_bandwidth - current_route_bandwidth, 2)
            updated_available = round(current_available_bandwidth + current_route_bandwidth, 2)
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = updated_allocation
            graph.graph[src][dst]['available_bandwidth'] = updated_available
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = updated_allocation
            graph.graph[dst][src]['available_bandwidth'] = updated_available
            
            #print(f'\nfrom {src} -> {dst}')
            #print(f'\nprevious allocated bandwidth: {current_allocated_bandwidth} Mbps')
            #print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
            #print(f'new allocated bandwidth: {updated_allocation} Mbps')
            #print(f'new available bandwidth: {updated_available} Mbps')
        
        route_set[source_id]['total_route_bandwidth'] -= current_allocated_bandwidth
        print(f'sucessfully deallocated bandwidth: {current_route_bandwidth} Mbps')
    
    
    @staticmethod
    def decrease_bandwidth_reservation(
        graph: 'Graph', route_set: dict, route: list, required_throughput: float
    ):
        print(f'\nDecreasing BW reservation to {required_throughput} Mbps for route:')
        #print(route)
        print(" -> ".join(route))
        source_node_id = route[0]
        for src, dst in NetworkController.__pairwise(route):
            
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
        
            updated_allocation = round(required_throughput, 2)
            updated_available = round(current_available_bandwidth + (current_allocated_bandwidth - required_throughput), 2)
            
            
            '''
            print(f'\nfrom {src} -> {dst}')
            print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
            print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
            print(f'new allocated bandwidth: {updated_allocation} Mbps')
            print(f'new available bandwidth: {updated_available} Mbps')
            '''
    
            if updated_available < 0:
                a = input('\n***CRASHED!***')
                return
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = updated_allocation
            graph.graph[src][dst]['available_bandwidth'] = updated_available
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = updated_allocation
            graph.graph[dst][src]['available_bandwidth'] = updated_available
            
        
        print(f'\nprevious route bandwidth: {route_set[source_node_id]["total_route_bandwidth"]} Mbps')
        route_set[source_node_id]['total_route_bandwidth'] = updated_allocation
        print(f'\nnew route bandwidth: {route_set[source_node_id]["total_route_bandwidth"]} Mbps')
        
    
    @staticmethod
    def increase_bandwidth_reservation(
        graph: 'Graph', route_set: dict, route: list, required_throughput: float
    ):
        print(f'\nIncreasing BW reservation to {required_throughput} Mbps for route:')
        #print(route)
        print(" -> ".join(route))
        source_node_id = route[0]
        for src, dst in NetworkController.__pairwise(route):
            
            #print(f'\nfrom {src} -> {dst}\n\n')
            #pprint(graph.graph)
            
            #a = input('')
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
        
            updated_allocation = round(current_allocated_bandwidth + (required_throughput - current_allocated_bandwidth), 2)
            updated_available = round(current_available_bandwidth - required_throughput, 2)
            
            '''
            print(f'\nfrom {src} -> {dst}')
            print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
            print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
            print(f'new allocated bandwidth: {updated_allocation} Mbps')
            print(f'new available bandwidth: {updated_available} Mbps')
            '''
    
            if updated_available < 0:
                a = input('\n***CRASHED!***')
                return
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = updated_allocation
            graph.graph[src][dst]['available_bandwidth'] = updated_available
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = updated_allocation
            graph.graph[dst][src]['available_bandwidth'] = updated_available
            
        print(f'\nprevious route bandwidth: {route_set[source_node_id]["total_route_bandwidth"]} Mbps')
        route_set[source_node_id]['total_route_bandwidth'] = updated_allocation
        print(f'new route bandwidth: {route_set[source_node_id]["total_route_bandwidth"]} Mbps')
    
    
    @staticmethod
    def route_congested(graph: 'Graph', route: list, required_throughput: float) -> bool:
        congested = False
        for src, dst in NetworkController.__pairwise(route):
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
            if current_available_bandwidth < required_throughput:
                congested = True
                break
        return congested
    
    
    @staticmethod
    def decrease_all_flow_resolutions(graph: 'Graph', route_set: dict, flow_set: dict, served_flows: list):
        #TODO: instead of decreasing all flow resolutions, we must look for all routes passing through the congested node and decrease the bandwidth of all routes passing through that node untill it satisfies at least one quota before the current quota.
        #TODO: after shifting all flow resolutions, we have to consider the current allocated throughput after the first iteration of this function. Consider also dealocating the route...
        
        print(f'\n*** DECREASING ALL FLOW RESOLUTIONS ***')
        print(f'served flows: {served_flows}')
        #print(f'flow set:')
        #pprint(flow_set)
        print(f'\n')
        pprint(route_set)
        print(f'\n')
        
        for served_flow in served_flows:
            print(f'*************************************************************')
            print(f'\n*** served flow: {served_flow} ***')
            source_node_id = 'BS' + str(flow_set[served_flow]['client'])
            if source_node_id not in route_set.keys():
                print(f'source node: {source_node_id}')
                print(f'key {source_node_id} not found in route_set')
                print(f'route_set keys: {route_set.keys()}')
                a = input('')
            
            current_route = route_set[source_node_id]['route']
            
            flow_throughput = flow_set[served_flow]['throughput']
            flow_previous_throughput = bitrate_profiles.get_previous_throughput_profile(flow_throughput)
            
            #print(f'source node: {source_node_id}')
            
            print(f'served flow throughput: {flow_throughput} Mbps')
            print(f'previous served flow throughput: {flow_previous_throughput} Mbps')
            print(" -> ".join(current_route))
            #print(f'current route: {current_route}')
            #print(f'current route throughput: {current_route_throughput} Mbps')
            #print(f'route info {current_route[0]} -> {current_route[-1]}:')
            #print(route_set[source_node_id])
            #print(f'graph info:')
            #pprint(graph.graph[current_route[0]])
            
            
            #a = input('')
            
            if flow_previous_throughput is None:
                print(f'*** NO ROUTE FOUND ***')
                print(f'Using the lowest throughput profile: {flow_throughput}')

            else:
                print(f'new flow throughput: {flow_previous_throughput} Mbps')
                flow_set[served_flow]['throughput'] = flow_previous_throughput
        
                route_set[source_node_id]['total_route_bandwidth'] -= flow_throughput - flow_previous_throughput
                
                a = input('\ntype to decrease BW and update plot\n')
                
                NetworkController.decrease_bandwidth_reservation(graph, route_set, current_route, flow_previous_throughput)
                
                generate_networks.plot_graph(graph.graph)
            
            a = input('')
        
        print(f'\n*** FINISH DECREASING ALL FLOW RESOLUTIONS ***')
        a = input('')
        
        
    @staticmethod
    def decrease_flow_resolution(
        graph: 'Graph', route_set: dict, flow_set: dict, served_flows: list, source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float
    ) -> dict:
        
        NetworkController.decrease_all_flow_resolutions(graph, route_set, flow_set, served_flows)
        print(f'*** recalculating a new route ***')
        previous_throughput = required_throughput
        required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
        if required_throughput is None:
            print(f'*** NO ROUTE FOUND ***')
            print(f'Using the lowest throughput profile: {previous_throughput}')
            required_throughput = previous_throughput
            #a = input('type to continue')
            return 
        
        #print(f'*** NEW BW PROFILE {required_throughput} ***')
        new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
            graph, source_node, target_node, required_throughput
        )    
        result = {
            'new_route': new_route,
            'route_max_throughput': route_max_throughput,
        }
        
        return result
        
    @staticmethod
    def allocate_bandwidth(
        graph: 'Graph', route_set: dict, source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float, flow_set: dict, served_flows: list
    ):
    
        source_node_id = source_node.bs_name
        
        new_route = None
        current_route = None
        
        if source_node_id not in route_set.keys():
            print(f'\nNEW ROUTE')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            while route_max_throughput == MIN_VALUE:
                
                print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                
                #NetworkController.decrease_all_flow_resolutions(graph, route_set, flow_set, served_flows)
            
                print(f'*** recalculating a new route ***')
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                if required_throughput is None:
                    print(f'\n*** NO ROUTE FOUND ***')
                    print(f'\nUsing the lowest throughput profile: {previous_throughput}')
                    required_throughput = previous_throughput
                    print(f'\n*** NEW BW PROFILE {required_throughput} ***')
                    break
                
                #print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
            
            print(" -> ".join(new_route))
            
            route_set[source_node_id] = {
                'route': new_route,
                'total_route_bandwidth': 0,
            }
            
        
        else:
            print(f'\nDEALLOCATING CURRENT ROUTE')
            current_route = route_set[source_node_id]['route']
            
            NetworkController.deallocate_bandwidth(
                graph, route_set, source_node_id
            )
            
            print(f'\nRECALCULATING A NEW ROUTE')
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            
            while route_max_throughput == MIN_VALUE:
                
                print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                
                #NetworkController.decrease_all_flow_resolutions(graph, route_set, flow_set, served_flows)
                
                #print(served_flows)
                #print(len(served_flows))
                #pprint(flow_set)
                #a = input('')
                print(f'\n*** recalculating a new route ***')
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                if required_throughput is None:
                    print(f'*** NO ROUTE FOUND ***')
                    print(f'Using the lowest throughput profile: {previous_throughput}')
                    required_throughput = previous_throughput
                    #a = input('type to continue')
                    return 
                
                print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                #print(f'*** NEW route_max_throughput: {route_max_throughput}')
                #generate_networks.plot_graph(graph.graph)
            
        
        #print(f'*** CURRENT route_max_throughput: {route_max_throughput}')                
        print(f'current route: {current_route}')
        
        a = input('\ntype to increase BW and update plot\n')
        
        NetworkController.increase_bandwidth_reservation(graph, route_set, new_route, required_throughput)
        
        generate_networks.plot_graph(graph.graph)
        

        return required_throughput
        
        
        
        
        
        
        
        
        
       
        
    
    @staticmethod
    def allocate_bandwidth_bk(
        graph: 'Graph', route_set: dict, source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float
    ):
    
        source_node_id = source_node.bs_name
        
        if source_node_id not in route_set.keys():
            #print(source_node_id)
            #print(route_set.keys())
            #a = input('')
            print(f'\nNEW ROUTE')
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            print(" -> ".join(new_route))
            
            route_set[source_node_id] = {
                'route': new_route,
                'total_route_bandwidth': 0,
            }

            NetworkController.increase_bandwidth_reservation(graph, route_set, new_route, required_throughput)
            
        else:
            current_route = route_set[source_node_id]['route']
            
            if not NetworkController.route_congested(graph, current_route, required_throughput):
                print(f'\nCURRENT ROUTE IS NOT CONGESTED')
                
                NetworkController.increase_bandwidth_reservation(graph, route_set, current_route, required_throughput)
        
            else:
                print(f'\nCURRENT ROUTE IS CONGESTED')
                
                updated_required_throughput = round(route_set[source_node_id]['total_route_bandwidth'] + required_throughput, 2)
                
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, updated_required_throughput
                )
                
                if route_max_throughput == MIN_VALUE:
                    """
                    TODO: here, we shouldn't use the same route, instead we recalculate the new route with a lower throughput. after the first trial,  we get the previous currespondent throughput based on required throughput and try it, if it doesn't work, we try the previous one and so on... an exception should be raised if we reach the minimum throughput possible and there is no more routes available.
                    """
                    print(f'\nNO MORE ROUTES AVAILABLE FOR THE PATH')
                    print(f'*** recalculating a suboptimal route ***')
                    a = input('')
                    while True:
                        updated_required_throughput = bitrate_profiles.get_previous_throughput_profile(updated_required_throughput)
                        new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                            graph, source_node, target_node, updated_required_throughput
                        )
                        if route_max_throughput != MIN_VALUE:
                            break
                    
                    print(f'\nNEW SUBOPTIMAL ROUTE FOUND!')
                    print(" -> ".join(new_route))

                    print(f'\nDEALLOCATING PREVIOUS ROUTE')
                    NetworkController.deallocate_bandwidth(
                        graph, route_set, source_node_id
                    )
                    
                    print(f'\nALLOCATING NEW ROUTE')
                    route_set[source_node_id] = {
                        'route': new_route,
                        'total_route_bandwidth': updated_required_throughput,
                    }
                        
                    NetworkController.increase_bandwidth_reservation(graph, route_set, new_route, updated_required_throughput)
                    
                
                else:
                    print(f'\nNEW ROUTE FOUND!')
                    print(" -> ".join(new_route))

                    print(f'\nDEALLOCATING PREVIOUS ROUTE')
                    NetworkController.deallocate_bandwidth(
                        graph, route_set, source_node_id
                    )
                    
                    print(f'\nALLOCATING NEW ROUTE')
                    route_set[source_node_id] = {
                        'route': new_route,
                        'total_route_bandwidth': updated_required_throughput,
                    }
                        
                    NetworkController.increase_bandwidth_reservation(graph, route_set, new_route, updated_required_throughput)
            
            
            
            '''
            current_route = route_set[source_node_id]['route']
            if not NetworkController.route_congested(graph, current_route, required_throughput):
                print(f'\nCURRENT ROUTE IS NOT CONGESTED')
                
                NetworkController.reserve_bandwidth(graph, route_set, current_route, required_throughput)
        
            else:
                print(f'\nCURRENT ROUTE IS CONGESTED')
                
                updated_required_throughput = round(route_set[source_node_id]['total_route_bandwidth'] + required_throughput, 2)
                
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, updated_required_throughput
                )
                
                if route_max_throughput == MIN_VALUE:
                    print(f'\nNO MORE ROUTES AVAILABLE FOR THE PATH')
                    print(f'*** recalculating a suboptimal route ***')
                    while True:
                    updated_required_throughput = NetworkController.get_previous_profile(updated_required_throughput)
                    new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                        graph, source_node, target_node, updated_required_throughput
                    )
                    if route_max_throughput != MIN_VALUE:
                        break
                pass
                    """
                    here, we shouldn't use the same route, instead we recalculate the new route with a lower throughput. after the first trial,  we get the previous currespondent throughput based on required throughput and try it, if it doesn't work, we try the previous one and so on... an exception should be raised if we reach the minimum throughput possible and there is no more routes available.
                    """
                    pass
                
                else:
                    print(f'\nNEW ROUTE FOUND!')
                    print(" -> ".join(new_route))

                    print(f'\nDEALLOCATING PREVIOUS ROUTE')
                    NetworkController.deallocate_bandwidth(
                        graph, route_set, source_node_id
                    )
                    
                    print(f'\nALLOCATING NEW ROUTE')
                    route_set[source_node_id] = {
                        'route': new_route,
                        'total_route_bandwidth': updated_required_throughput,
                    }
                        
                    NetworkController.reserve_bandwidth(graph, route_set, new_route, updated_required_throughput)
            '''
        
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
        
        
    
    #TODO: to be tested
    @staticmethod
    def generate_network_plot(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        #TODO: this function should receive the network graph and plot the connections between them and the available bandwidth over time. 
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
            #TODO: before each iteration, update the HMDs positions...
            NetworkController.generate_network_plot(base_station_set, hmds_set)