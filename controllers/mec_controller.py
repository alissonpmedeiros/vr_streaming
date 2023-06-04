import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.graph import Graph 
    from models.base_station import BaseStation
    from models.quotas import Quota
    
from models.mec import Mec 
from models.hmd import VrService 

from models.video import Video
from models.video import VideoServer
from models.bitrates import BitRateProfiles


""" controller modules """
from controllers import bs_controller 
from controllers import json_controller
from controllers import config_controller
from controllers import dijkstra_controller

""" other modules """
import uuid
from typing import Dict
from numpy import random
from pprint import pprint as pprint

BITRATE_THROUGHPUT_PROFILES = BitRateProfiles.get_throughput_profiles()

CONFIG = config_controller.ConfigController.get_config()

""" lam: rate or known number of occurences """
gpu_lam: int = CONFIG['MEC_SERVERS']['GPU_LAM']
cpu_lam: int = CONFIG['MEC_SERVERS']['CPU_LAM']


class MecResourceController:
    """ generates MEC GPU and CPU workloads """

    @staticmethod
    def generate_cpu_resources(number_mecs: int):
        """generates cpu resources for MEC servers"""
        
        cpu_set = random.poisson(cpu_lam, number_mecs)
        return cpu_set
        
    @staticmethod
    def include_zero_values(array) -> None:
        """ randomly set zero values for GPUs on MEC servers """
        
        array_len  = len(array)
        #percentage = int(array_len / 3.33) #defines 30% of the array with zero values
        servers_without_gpus = CONFIG['MEC_SERVERS']['MECS_WITHOUT_GPUS']
        for i in range(0, servers_without_gpus):
            while True:
                random_index = random.randint(0,array_len)
                if array[random_index] != 0:
                    array[random_index] = 0
                    break
        return

    @staticmethod
    def generate_gpu_resources(number_mecs: int):
        """generates gpu resources for MEC servers"""
        gpu_set = random.poisson(lam=gpu_lam, size=number_mecs)
        MecResourceController.include_zero_values(gpu_set)
        return gpu_set
    

class MecController:
    """ represents a MEC controller for MEC servers """

    @staticmethod 
    def discover_mec(
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str, Mec], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: VrService
    ) -> Dict[str, Mec]:
        """ discovers a MEC server for a VR service """ 
        
        mec_dict: Dict[str, Mec] = {
            'id': None,
            'mec': None
        }   
        
        shortest_path = shortest_path = dijkstra_controller.DijkstraController.get_ETE_zone_shortest_path(
            mec_set, graph, start_node
        )
        
        # Iterate over the sorted shortest path (list of tuples) and checks whether a mec server can host the service
        for node in shortest_path:    
            bs_name = node[0]
            bs =  bs_controller.BaseStationController.get_base_station_by_name(base_station_set, bs_name)
            base_station: BaseStation = bs.get('base_station')
            bs_mec = MecController.get_mec(mec_set, base_station)
            
            if MecController.check_deployment(bs_mec, service):
                mec_dict.update({'id': base_station.mec_id, 'mec': bs_mec})
                break
            
        #if mec_dict.get('mec') is None:
            #print(f'\nALL MEC servers are overloaded! Discarting...')
        
        return mec_dict
    
    

    @staticmethod
    def init_static_services(mec: Mec) -> None:
        """ creates services that will be deployed on mec server i """
        
        while True:
            cpu_only = False
            if mec.overall_gpu == 0:
                cpu_only = True

            new_service = VrService(cpu_only=cpu_only)

            if MecController.check_available_resources(mec, new_service):
                MecController.deploy_service(mec, new_service)
            else:
                break
        return 

    @staticmethod
    def create_mec_servers(base_station_set: Dict[str, 'BaseStation'], overall_mecs: int) -> None:
        """ inits mec servers with their services"""
        
        mec_set = {
            "mec_set": {}
        }

        cpu_set = MecResourceController.generate_cpu_resources(overall_mecs)
        gpu_set = MecResourceController.generate_gpu_resources(overall_mecs)
        init_resource_load = CONFIG['MEC_SERVERS']['INIT_RESOURCE_LOAD']
        
        
        for i in range(0, overall_mecs):
            bs_id = str(i)
            bs: 'BaseStation' = base_station_set[bs_id]
            #mec_id = str(uuid.uuid4())
            mec_id = i
            mec_name = 'MEC' + str(i)
            overall_mec_cpu = int(cpu_set[i])
            overall_mec_gpu = int(gpu_set[i])
            computing_latency = bs.node_latency
            server: VideoServer = VideoServer()
            number_of_videos = CONFIG['MEC_SERVERS']['NUMBER_OF_VIDEOS']
            MecController.init_video_server_videos(server, number_of_videos)
            
            new_mec = Mec(
                name=mec_name, 
                overall_cpu=overall_mec_cpu, 
                overall_gpu=overall_mec_gpu, 
                computing_latency=computing_latency, 
                init_resource_load=init_resource_load,
                video_server=server
            )
            
            mec_set["mec_set"][mec_id] = new_mec

        for mec in mec_set["mec_set"].values():
            MecController.init_static_services(mec)

        json_controller.EncoderController.encoding_to_json(mec_set)
        return

    @staticmethod
    def get_mec(mec_set: Dict[str, Mec], base_station: 'BaseStation') -> Mec:
        """ gets a MEC server attached to a base station"""
        
        mec_id = base_station.mec_id
        return mec_set[mec_id]

    @staticmethod
    def check_available_resources(mec: Mec, service: VrService ) -> bool:
        """ checks resource availity at MEC server. """   
        quota: Quota = service.quota
        if quota.resources['cpu'] + mec.allocated_cpu <= mec.cpu_threshold and quota.resources['gpu'] + mec.allocated_gpu <= mec.gpu_threshold:
            """ returns True if there is available resources after deploy a vr service """
            return True
        return False

    @staticmethod
    def check_deployment(mec: Mec, service: VrService) -> bool:
        """ checks if a service can be deployed on mec server i on the fly """
        
        quota = service.quota
        if quota.resources['cpu'] + mec.allocated_cpu <= mec.overall_cpu and quota.resources['gpu'] + mec.allocated_gpu <= mec.overall_gpu:
            return True
        return False

    @staticmethod
    def deploy_service(mec: Mec, service: VrService) -> None:
        """ deploys a vr service on mec server """
        mec.allocated_cpu += service.quota.resources['cpu']
        mec.allocated_gpu += service.quota.resources['gpu']
        mec.services_set.append(service)
        return

    @staticmethod
    def remove_service(mec: Mec, service: VrService) -> VrService:
        """ removes a service from where it is deployed """
        extracted_service: VrService = None
        service_index = [mec_service.id for mec_service in mec.services_set].index(service.id)
        extracted_service = mec.services_set.pop(service_index)
        
        mec.allocated_cpu -= extracted_service.quota.resources['cpu']
        mec.allocated_gpu -= extracted_service.quota.resources['gpu']
                
        return extracted_service

    @staticmethod
    def get_mec_service(mec_set: Dict[str, Mec], service_id: str) -> VrService:
        """ gets a VrService that is deployed on mec server """
        
        for mec in mec_set.values():
            for service in mec.services_set:
                if service.id == service_id:
                    return service
        return None

    @staticmethod 
    def get_service_mec_server(mec_set: Dict[str, Mec], service_id: str) -> Dict[str, Mec]: 
        """ gets the mec server where the service is deployed and its ID """
        
        mec_dict: Dict[str, Mec] = {
            'id': None,
            'mec': None
        }
        
        for id, mec in mec_set.items():
            for service in mec.services_set:
                if service.id == service_id:
                    mec_dict.update({'id': id, 'mec': mec})
                    break
                
        return mec_dict

    @staticmethod
    def get_service_bs(
        base_station_set: Dict[str,'BaseStation'], mec_set: Dict[str, Mec], service_id: str
    ) -> 'BaseStation':
        """ gets the base station where the mec (used to deploy the service) is attached to """
        
        mec_server: Dict[str, Mec] = MecController.get_service_mec_server(mec_set, service_id) 
        service_mec_server_id: str = mec_server.get('id')

        for base_station in base_station_set.values():
            if base_station.mec_id == service_mec_server_id:
                return base_station
        return None

    @staticmethod
    def get_mec_bs_location(base_station_set: Dict[str,'BaseStation'], mec_id: str) -> 'BaseStation':
        """ gets the base station location where the mec is attached to """
        for base_station in base_station_set.values():
            if base_station.mec_id == mec_id:
                return base_station
        return None


####################################################################################

#class MecController:
    @staticmethod
    def get_video_server(mec_set: Dict[str, 'Mec'], server_id: str):
        
        for mec in mec_set.values():
            if server_id == mec.video_server.id:
                return mec.video_server 
        print('SERVER NOT FOUND!')
        return None
    
    @staticmethod
    def get_video_server_by_video_id(mec_set: Dict[str, 'Mec'], video_id: str) -> VideoServer:
        """returns a server object that contains the video_id"""
        
        for mec in mec_set.values():
            if video_id in mec.video_server.video_set.keys():
                return mec.video_server
        
        print('SERVER NOT FOUND!')
        return None
    
    @staticmethod
    def add_video(mec_set: Dict[str, 'Mec'], server_id: str, video: 'Video'):
        server: VideoServer = MecController.get_video_server(mec_set, server_id)
        server.video_set[video.id] = video
        #print(server)
        #a = input('')
        return None
    
    def init_video_server_videos(server: VideoServer, number_of_videos: int):
        """creates a video and adds it to the server"""
        #TODO: need to change the video duration and refresh rate for each video
        #server: VideoServer = MecController.get_server(mec_set, server_id)
        duration = 100
        refresh_rate = 120
        for i in range(number_of_videos):
            video = Video(duration=duration, refresh_rate=refresh_rate)
            server.video_set[video.id] = video
        return None
    
    @staticmethod
    def get_video(mec_set: Dict[str, 'Mec'], server_id: str, video_id: str) -> 'Video':
        server:VideoServer = MecController.get_video_server(mec_set, server_id)
        return server.video_set[video_id]
    
    @staticmethod
    def __encode_video(server: VideoServer, video: 'Video'):
        """ encode the video into several resolutions and bitrates """
        
        encoded_video = {
            'bitrates': {}
        }
       
        for throughput, values in BITRATE_THROUGHPUT_PROFILES.items():
            min_bitrate = throughput
            video_size = min_bitrate * video.duration
            number_segments = int(video.duration / server.segmentation_time)
            segment_size = round((video_size / number_segments), 2)
            
            encoded_video['bitrates'][min_bitrate] = {        
                'resolution': values['resolution'],
                'frame_rate': values['frame_rate'],
                'video_size': video_size,
                'number_segments': number_segments,
                'segment_size': segment_size,
                'video_segments': []
            }
        
        
        return encoded_video
    
    @staticmethod
    def __segment_video(encoded_video: dict):
        """ segment video """
        for key, values in encoded_video['bitrates'].items():
            number_segments = values['number_segments']
            segment_size = values['segment_size']
            
            for segment in range(number_segments):
                values['video_segments'].append(segment_size)
                
        return encoded_video
    
    @staticmethod
    def __build_manifest(video: 'Video', segmented_video: dict):
        """ get video manifest """
        manifest = {
            'video_duration': video.duration,
            'video_frame_rate': video.refresh_rate,
            'bitrates': {}
        }
        
        for key, values in segmented_video['bitrates'].items():
            manifest['bitrates'][key] = {
                'resolution': values['resolution'],
                'frame_rate': values['frame_rate'],
                'video_size': values['video_size'],
                'number_segments': values['number_segments'],
                'segment_size': values['segment_size'],
            }
            
        return manifest
    
    @staticmethod
    def get_manifest(mec_set: Dict[str, 'Mec'], video_id: str):
        server:VideoServer = MecController.get_video_server_by_video_id(mec_set, video_id)
        video:Video = MecController.get_video(mec_set, server.id, video_id)
        print(f'encoding video')
        encoded_video = MecController.__encode_video(server, video)
        print(f'segmenting video')
        segmented_video = MecController.__segment_video(encoded_video)
        print(f'packaging video')
        manifest = MecController.__build_manifest(video, segmented_video)
        print(f'manifest sent to client')
        return manifest
    
    #TODO: check this method
    @staticmethod
    def get_segment(mec_set: Dict[str, 'Mec'], video_id: str, segment: int):
        server:VideoServer = MecController.get_video_server_by_video_id(mec_set, video_id)
        video:Video = MecController.get_video(mec_set, server.id, video_id)
        encoded_video = MecController.__encode_video(server, video)
        segmented_video = MecController.__segment_video(encoded_video)
        
        return segmented_video['bitrates'][video.refresh_rate]['video_segments'][segment]
    
    '''
    @staticmethod
    def get_servers_keys(servers_set: Dict[str, 'Video']):
        key_list = []
        for key in servers_set.keys():
            key_list.append(key)
        
        return key_list
    '''
    
    @staticmethod
    def print_video_servers(mec_set: Dict[str, 'Mec']):
        #print(f'\nServers: {len(servers_set)}')
        for mec in mec_set.values():
            print(f'\nvideo server: {mec.video_server.id}')
            print('video set:')
            for video_id, video_metadata in mec.video_server.video_set.items():
                pprint(video_metadata)
            