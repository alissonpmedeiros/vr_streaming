""" other modules """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List


@dataclass_json
@dataclass
class BaseStation:
    """represents a base station"""
    id: str
    bs_name: str
    node_label: str
    node_latency: float
    wireless_latency: float
    signal_range: float
    position: List[float] = field(default_factory=list, init=True)
    edges: List[str] = field(default_factory=list, init=True)
    edge_net_latencies: List[float] = field(default_factory=list, init=True)
    edge_net_throughputs: List[float] = field(default_factory=list, init=True)
    mec_id: str = field(default= None, init=False)
    #links: dict = field(default_factory=dict, init=True)
    #wireless_latency: float = field(default_factory=float, init=True)
   
    
   