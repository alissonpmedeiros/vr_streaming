import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.hmd import VrHMD 
    from models.graph import Graph 
    from models.hmd import VrService 
    from models.base_station import BaseStation 
    
from models.migration_ABC import Migration

""" controller modules """
from controllers import hmd_controller 
from controllers import bs_controller 
#from controllers import scg_controller 
from controllers import mec_controller
from controllers import dijkstra_controller 

"""other modules"""
import sys
from typing import Dict
from pprint import pprint as pprint

CDN_SERVER_ID = 136

class LA(Migration):
    """provides a network latency aware (LA) service migration algorithm that considers the resources of the MECs before performing migrations"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(
            base_station_set, mec_set, hmds_set, graph
        )

    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return self.perform_migration(
            base_station_set, mec_set, hmds_set, graph, service
        )
        
    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> Dict[str,'Mec']:
        """ discovers a nearby MEC server to either offload or migrate the service not considering the resource availaiblity of MEC nodes"""
        #print(f'\ndiscovering mec')
        mec_dict: Dict[str,'Mec'] = {
            'id': None,
            'mec': None
        }
        
        shortest_path = dijkstra_controller.DijkstraController.get_all_E2E_shortest_paths(
            graph, start_node
        )
        
        for node in shortest_path:    
            
            bs_id = node[0][2:]
            base_station: BaseStation = base_station_set[bs_id]
            bs_mec: Mec = mec_set[str(base_station.mec_id)]
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                mec_dict.update({'id': base_station.mec_id, 'mec': bs_mec})
                return mec_dict
        
        if not mec_dict.get('mec'):
            print(f'\nALL MEC servers are overloaded! Discarting...')
        #    a = input('')
        
        return mec_dict

    def perform_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between hmd_ip and where the service is deployed
        """
        #print(f'\nperforming migration\n')
        service_owner_hmd: 'VrHMD' = hmd_controller.HmdController.get_vr_service_owner(
            hmds_set, service
        )
        #print(f'\nservice hmd owner {service_owner_hmd.id}')
        
        
        
        hmd_base_station: 'BaseStation' = base_station_set[str(service_owner_hmd.current_base_station)]
        
        service_mec_server: 'Mec' = None
        service_mec_server_bs: 'BaseStation' = None
        if service_owner_hmd.service_offloading:        
            service_mec_server = mec_set[str(service_owner_hmd.offloaded_server)]
            service_mec_server_bs = base_station_set[str(service_owner_hmd.offloaded_server)]
            
        #print(f'\nHMD is connected to base station {hmd_base_station.id}')
        #print(f'\nHMD was connected to base station {service_owner_hmd.previous_base_station}')
        #print(f'\nHMD services  are deployed on mec server {service_mec_server.name}')
        #print(f'\nMEC server {service_mec_server.name} is connected to base station {service_mec_server_bs.id}')
        
        
        
        dst_node: Dict[str, 'Mec'] = self.discover_mec(
            base_station_set, 
            mec_set, 
            graph, 
            hmd_base_station, 
            service,
        )
        
        mec_candidate_id: int = dst_node.get('id')
        mec_candidate: 'Mec' = dst_node.get('mec')
        if not mec_candidate:
            #print(f'\nNo mec server available for migration!')
            self.unsuccessful_migrations += 1
            return False
        candidate_base_station = base_station_set[str(mec_candidate_id)]
        #print(f'\nCandidate mec server: {mec_candidate.name} | current_mec_server: {service_mec_server.name}')
        
        
        if mec_candidate and mec_candidate.name != service_mec_server.name:
            '''
            '''
            path, latency_from_hmd_to_service_mec_server = dijkstra_controller.DijkstraController.get_shortest_path(
                graph, hmd_base_station, service_mec_server_bs
            )  
            #print(f'\nWireless latency from hmd_base_station: {hmd_base_station.wireless_latency}')
            #print(f'\nLatency from hmd to service mec server: {latency_from_hmd_to_service_mec_server}')
            #print(' -> '.join(path))
            
            
                
            cdn_base_station = base_station_set[str(CDN_SERVER_ID)]
            #print(f'\nCDN base station: {cdn_base_station.id}')
            current_path, current_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(graph, cdn_base_station, service_mec_server_bs)
            current_latency += latency_from_hmd_to_service_mec_server
            #print(f'\nCurrent latency: {current_latency}')
            current_path.reverse()
            #print(' -> '.join(current_path))
            
            
            path, latency_from_hmd_to_candidate_mec_server = dijkstra_controller.DijkstraController.get_shortest_path(
                graph, hmd_base_station, candidate_base_station
            ) 
            candidate_path, candidate_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(graph, cdn_base_station, candidate_base_station)
            candidate_latency += latency_from_hmd_to_candidate_mec_server
            
            #print(f'\nCandidate latency: {candidate_latency}')
            candidate_path.reverse()
            #print(' -> '.join(candidate_path))
            
            if candidate_latency < current_latency:
                #a = input('')
                #print(f'\nservice {service.id} is being migrated from {service_mec_server.name} to {mec_candidate.name}\n')
                #print(f'\nbefore migration')
                #pprint(service_mec_server.services_set)
                #print(f'\n\n')
                #pprint(mec_candidate.services_set)
                service_owner_hmd.offloaded_server = mec_candidate_id
                extracted_service = mec_controller.MecController.remove_service(
                    service_mec_server, service 
                )
                
                mec_controller.MecController.deploy_service(
                    mec_candidate, extracted_service
                )
                
                #print(f'\nafter migration')
                #pprint(service_mec_server.services_set)
                #print(f'\n\n')
                #pprint(mec_candidate.services_set)
                #a = input('')
                self.successful_migrations += 1
                return True
            
            return False
            
            
        else:
            self.unsuccessful_migrations += 1
            return False
        
        
        
        '''
        if mec_candidate:
            
            current_latency: dict = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
                graph, hmd_base_station, service_mec_server
            )
        
            current_service_latency = current_latency.get('e2e_latency')
            
            extracted_service = mec_controller.MecController.remove_service(
                service_mec_server, service
            )
        
            candidate_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
                graph, hmd_base_station, base_station_candidate
            )

            candidate_service_latency = candidate_latency.get('e2e_latency')
            
            print('\n hmd connected to base station: ', hmd_base_station.id)
            print(f'\nCurrent service latency: {current_service_latency} at MEC {service_mec_server.id}')
            print(f'\nCandidate service latency: {candidate_service_latency} at MEC {mec_candidate_id}')
            
            a = input('')
            
            if current_service_latency > candidate_service_latency:
                mec_controller.MecController.deploy_service(
                    mec_candidate, extracted_service
                )
                self.successful_migrations += 1
                return True
            
            mec_controller.MecController.deploy_service(
                service_mec_server, extracted_service
            )
            self.unsuccessful_migrations += 1
            return False
        else:
            self.unsuccessful_migrations += 1
            return False
        '''

            
    
        #if mec_candidate_id or mec_candidate is None:
        #    self.unsuccessful_migrations +=1
        #    return False