import typing 
if typing.TYPE_CHECKING:
    from video import Video

from models.quotas import Quota
""" other modules """
import uuid, random
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from pprint import pprint as pprint



#these quotas are not consided to be used during MEC server intialization
QUOTAS_CPU_SET = ['large', 'substantial', 'plentiful', 'ample', 'extensive', 'huge', 'massive', 'grant', 'giant', 'king', 'jumbo', 'xlarge']


'''
# TODO: this method should hav ethe same number of all possible resolutions with all possible refresh rates
@dataclass_json
@dataclass
class VideoDecoderEnergy:
    """ describes the energy consumption of the decoder """
    
    energy_consumption: str = field(default_factory=str, init=True)
    
    def set_energy(self, resolution_name: str):
        self.energy_consumption = self.get_energy(resolution_name)
    
    def get_energy(self, resolution_name: str):
        default = "incorrect energy"
        return getattr(self, 'energy_' + str(resolution_name), lambda: default)()

    def energy_1080p(self):
        return  1.63
    
    def energy_1440p(self):
        return 1.69
    
    def energy_4k(self):
        return 2.12
    
    def energy_8k(self):
        return 4.28    
'''
    

@dataclass_json
@dataclass
class VideoDecoder:
    """describes the energy of the decoder"""
    name: str = field(default_factory=str, init=True)
    
    '''
    energy: VideoDecoderEnergy = field(default_factory=VideoDecoderEnergy, init=True) 
    
    def __post_init__(self):
        self.energy = VideoDecoderEnergy()
    
    def set_energy_consumption(self, resolution_name: str):
        self.energy.set_energy(resolution_name)
    '''


@dataclass_json
@dataclass
class VrService:
    """ represents a VR service""" 
    id: str = field(default_factory=str, init=True)
    cpu_only: bool = field(default=False, init=True) 
    is_mobile: bool = field(default=False, init=True) 
    quota: Quota = field(default_factory=Quota, init=True)
    video_decoder: VideoDecoder = field(default_factory=VideoDecoder, init=True)
    
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
            quotas_set = Quota.get_quotas_set()
            
            """ if cpu_only is True, then the quotas 'large' and 'xlarge' are excluded """
            if self.cpu_only:
                """ selects a random quote for each service """
                quota_choice = random.choice(
                    [quota for quota in quotas_set if quota not in QUOTAS_CPU_SET]
                )
                self.quota = Quota(quota_choice)
            else:
                quota_choice = random.choice(quotas_set)
                self.quota = Quota(quota_choice)
            
            #self.video_decoder = VideoDecoder()
            #resolution_name = random.choice(RESOLUTION_SET)        
            #self.video_decoder.set_energy_consumption(resolution_name)
        

@dataclass_json
@dataclass
class VideoClient:
    buffer_size:int = 0 # Maximum buffer size in seconds
    refresh_rate:int = 0
    missed_frames:int = 0
    data_received:float = 0
    playback_time:int = 0
    current_buffer:int = 0 # Current buffer size in seconds
    current_throughput:int = 0
    video_id: str = field(default_factory=str, init=True)
    video_quality: str = field(default_factory=str, init=True)
    
    def __check_net_bandwidth():
        pass
        '''
        max_throughput = <= RWIN/RTT
        where, RWIN = TCP receive window size
        and RTT = round trip time
        
        EXAMPLE:
        let us assume that RWIN = 65,535 bytes
        RTT is 0.220 seconds -> multiply the time value by 1000 to convert it to milliseconds or divide by 1000 from milliseconds to seconds
        
        Result:  
        Max Bandwidth = 65,535 bytes(64KB) / 0.220 s = 297886.36 B/s * 8 = 2.383 Mbit/s
        '''
    def __get_available_throughput():
        pass
        '''
        We have to estimate the available throughput:
        
        available throughput = available bandwidth / overhead
        
        Here, overhead refers to the amount of bandwidth used by the protocol headers and other control information.
        
        Typically, the overhead for HTTP is typically around 10% under 1mbps. Let us assume the HTTP overhead is 3%.
        
        Thus:
        available throughput = available bandwidth(Mbps) / overhead (available bandwidth * 0.03)
        '''
        
        '''
        desired bitrate = available throughput * segment duration / segment size
        
         The next step is to select the appropriate bitrate. This can be done by comparing the desired bitrate with the bitrates available in your video library and selecting the closest match.
         
         Here we should get the abs profiles...
        '''
    
    def __calculate_video_bitrate():
        pass
        '''
        video bitrate = (Resolution (3840 x 2160 for 4K) x Frame Rate (60) x Bit Depth (10) * compression ratio)/ 100**2 in Mbps 
        '''
    
    def __select_resolution():
        pass
        '''
        select the resolution based on the available bitrate
        '''   
    
    def __throughput_based_algorithm():
        '''
        throughput-based algorithm logic:
        
        1. Check the network bandwidth
        2. calculate the available throughput
        3. calculate the desired bitrate: bandwidth should match the banwidth in bitrate profiles
        4. select the video resolution
        '''
    
    def __buffer_based_algorithm():
        pass
    
    def __download_segment():
        pass
    
    def __decode_segment():
        pass    
    
    def __play_segment():
        pass
    
    def __check_hmd_capacity():
        '''we have to implement a method to consider the HMD load in terms of GPU or CPU usage. In the traditional scenario, the whenever the load is too high then the refresh rate is decreased. Thus, the frame rate can be a nice metric to keep an eye. Besides, the new method has to consider the latency of the HMD and not only the load.'''
        pass
    
    def video_playback(video: 'Video'):
        # we should specify here the ABS algorithm to be used...
        pass

@dataclass_json
@dataclass
class VrHMD:
    """ represents a VR HMD instance """
    id: str = field(default_factory=str, init=True)
    signal_range: int = field(default_factory=int, init=True)
    computing_latency: float = field(default_factory=float, init=True)
    #cpu: int = 0
    #gpu: int = 0
    current_base_station: str = '' 
    previous_base_station: str = ''
    offloaded_server: str = ''
    position: List[float] = field(default_factory=list, init=True)
    video_client: VideoClient = field(default_factory=VideoClient, init=True)
    services_ids: List[str] = field(default_factory=list, init=True)
    services_set: List[VrService] = field(default_factory=list, init=True)
    
    
    

'''
if "__main__" == __name__:
    position = [1, 1]
    signal_range = 10
    computing_latency = 10
    
    hmd: VrHMD = VrHMD(
                signal_range=signal_range,
                computing_latency=computing_latency,
                position=position
            )
    pprint(hmd)
'''

    #service = VrService(cpu_only=True)
    #pprint(service)
