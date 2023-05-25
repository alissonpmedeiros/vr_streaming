import typing
if typing.TYPE_CHECKING:
    from models.mec import Mec

from models.video import Video
from models.video import VideoServer
from models.bitrates import BitRateProfiles
from pprint import pprint as pprint
from typing import Dict

BITRATE_THROUGHPUT_PROFILES = BitRateProfiles.get_throughput_profiles()

class ServerController:
    
    @staticmethod
    def add_server(mec_set: Dict[str, 'Mec'], servers_set: Dict[str, VideoServer]):
        server: VideoServer = VideoServer()
        servers_set[server.id] = server
    
    @staticmethod
    def get_server(servers_set: Dict[str, VideoServer], server_id: str):
        #print(f'\nreceiving request\n')
        #print(server_id)
        #print(servers_set)
        #a = input('')
        if server_id  in servers_set.keys():
            #print('GOT IT!')
            #print(servers_set[server_id] )
            #a = input('')
            return servers_set[server_id] 
        print('SERVER NOT FOUND!')
        #a = input('')
        return None
    
    @staticmethod
    def get_server_by_video_id(servers_set: Dict[str, VideoServer], video_id: str) -> VideoServer:
        """returns a server object that contains the video_id"""
        for key, values in servers_set.items():
            #print(f'\ngeting server by video id\n')
            #print(key)
            #print(values)
            #print(type(values))
            
            if video_id in values.video_set.keys():
                #print(f'\nwe got a MATCH!\n')
                #print(values)
                #a = input('press enter to continue')
                return values
        print('SERVER NOT FOUND!')
        return None
    
    @staticmethod
    def add_video(servers_set: Dict[str, VideoServer], server_id: str, video: 'Video'):
        server: VideoServer = ServerController.get_server(servers_set, server_id)
        server.video_set[video.id] = video
        #print(server)
        #a = input('')
        return None
    
    def init_server_videos(servers_set: Dict[str, VideoServer], server_id: str):
        """creates a video and adds it to the server"""
        server: VideoServer = ServerController.get_server(servers_set, server_id)
        duration = 100
        refresh_rate = 120
        video = Video(duration=duration, refresh_rate=refresh_rate)
        server.video_set[video.id] = video
        return None
    
    @staticmethod
    def get_video(servers_set: Dict[str, VideoServer], server_id: str, video_id: str) -> 'Video':
        server:VideoServer = ServerController.get_server(servers_set, server_id)
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
    def get_manifest(servers_set: Dict[str, VideoServer], video_id: str):
        server:VideoServer = ServerController.get_server_by_video_id(servers_set, video_id)
        video:Video = ServerController.get_video(servers_set, server.id, video_id)
        print(f'encoding video')
        encoded_video = ServerController.__encode_video(server, video)
        print(f'segmenting video')
        segmented_video = ServerController.__segment_video(encoded_video)
        print(f'packaging video')
        manifest = ServerController.__build_manifest(video, segmented_video)
        print(f'manifest sent to client')
        return manifest
    
    #TODO: check this method
    @staticmethod
    def get_segment(servers_set: Dict[str, VideoServer], video_id: str, segment: int):
        server:VideoServer = ServerController.get_server_by_video_id(servers_set, video_id)
        video:Video = ServerController.get_video(servers_set, server.id, video_id)
        encoded_video = ServerController.__encode_video(server, video)
        segmented_video = ServerController.__segment_video(encoded_video)
        
        return segmented_video['bitrates'][video.refresh_rate]['video_segments'][segment]
    
    
    @staticmethod
    def get_servers_keys(servers_set: Dict[str, 'Video']):
        key_list = []
        for key in servers_set.keys():
            key_list.append(key)
        
        return key_list
    
    @staticmethod
    def print_servers(servers_set: Dict[str, VideoServer]):
        print(f'\nServers: {len(servers_set)}')
        for key, values in servers_set.items():
            print(f'\nvideo server: {key}')
            print('video set:')
            for video_id, video_metadata in values.video_set.items():
                pprint(video_metadata)
            '''
            '''
                
            
    
    
    