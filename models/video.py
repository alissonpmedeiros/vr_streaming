"""other modules"""
import uuid
from typing import Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from pprint import pprint as pprint


@dataclass_json
@dataclass
class VideoResolution:
    """describes the resolution of the video"""
    
    resolution: str = field(default_factory=str, init=True)
    
    def set_resolution(self, resolution_name: str):
        self.resolution = self.get_resolution(resolution_name)
    
    def get_resolution(self, resolution_name: str):
        default = "incorrect resolution"
        return getattr(self, 'resolution_' + str(resolution_name), lambda: default)()
    
    def resolution_8k(self):
        return "8k"
    
    def resolution_4k(self):
        return "4k"
    
    def resolution_1440p(self):
        return "1440p"
    
    def resolution_1080p(self):
        return "1080p"

@dataclass_json
@dataclass
class Video:
    
    id: str = field(default_factory=str, init=True)
    duration: float = field(default_factory=float, init=True)
    refresh_rate: int = field(default_factory=int, init=True)
    played_segment = 0
    resolution: VideoResolution = field(default_factory=VideoResolution, init=True)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass_json
@dataclass
class VideoServer:
    id: str = field(default_factory=str, init=True) 
    segmentation_time: int = 2 # 2 seconds  
    video_set: Dict[str, Video] = field(default_factory=dict, init=True)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())    
        
        
        
'''
if '__main__'== __name__:
    server = VideoServer()
    #pprint(server)
    
    duration = 100
    refresh_rate = 120
    video = Video(duration=duration, refresh_rate=refresh_rate)
    
    pprint(video)
'''