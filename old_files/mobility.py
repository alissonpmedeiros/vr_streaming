import time
import numpy as np
import matplotlib.pyplot as plt


plt.figure(figsize=(12, 12))

class BaseStation:
    def __init__(self, id, x, y, signal_range):
        self.id = id
        self.x = x
        self.y = y
        self.signal_range = signal_range

    def __repr__(self):
        return f"BaseStation({self.id}, {self.x}, {self.y}, {self.signal_range})"

class HMD:
    def __init__(self, id, x, y, signal_range):
        self.id = id
        self.x = x
        self.y = y
        self.signal_range = signal_range
        self.previous_base_station = None
        self.current_base_station = None

    def __repr__(self):
        return f"HMD({self.id}, {self.x}, {self.y}, {self.signal_range}, {self.current_base_station})"

    # ALREADY IMPLEMENTED!
    def connect_to_base_station(self, base_stations):
        max_signal_range = -1
        connected_base_station = None
        for base_station in base_stations:
            distance = np.sqrt((self.x - base_station.x)**2 + (self.y - base_station.y)**2)
            if distance <= base_station.signal_range and base_station.signal_range > max_signal_range:
                max_signal_range = base_station.signal_range
                connected_base_station = base_station
        
        if connected_base_station is None:
            self.current_base_station = self.previous_base_station
        
        else:
            self.previous_base_station = self.current_base_station
            self.current_base_station = connected_base_station


# ALREADY IMPLEMENTED! 
def generate_base_stations(num_base_stations, signal_range):
    base_stations = []
    for i in range(num_base_stations):
        x = np.random.rand()
        y = np.random.rand()
        #print(f'id: {i} -> x: {x}, y: {y}')
        base_station = BaseStation(i, x, y, signal_range)
        base_stations.append(base_station)
    #a = input('')
    return base_stations


# ALREADY IMPLEMENTED!
def generate_hmds(num_hmds, signal_range):
    hmds = []
    for i in range(num_hmds):
        x = np.random.rand()
        y = np.random.rand()
        hmd = HMD(i, x, y, signal_range)
        hmds.append(hmd)
    return hmds


# ALREADY IMPLEMENTED!
def print_network(base_stations, hmds):
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title("Network Graph")
    plt.xlabel("X")
    plt.ylabel("Y")
    
    for base_station in base_stations:
        circle = plt.Circle((base_station.x, base_station.y), base_station.signal_range, color='blue', alpha=0.1)
        plt.gca().add_patch(circle)
        plt.scatter(base_station.x, base_station.y, color='blue', marker='o')
        plt.annotate('BS{}'.format(base_station.id), xy=(base_station.x, base_station.y), ha='center', va='bottom', color='black')

    for hmd in hmds:
        circle = plt.Circle((hmd.x, hmd.y), hmd.signal_range, color='red', alpha=0.1)
        plt.gca().add_patch(circle)
        plt.scatter(hmd.x, hmd.y, color='red', marker='x')
        plt.annotate('HMD{}'.format(hmd.id), xy=(hmd.x, hmd.y), ha='center', va='bottom', color='black')
    
    plt.pause(0.01)
    plt.clf()
    #plt.show(block=False)
    #fig.canvas.draw()

# ALREADY IMPLEMENTED! 
def update_hmd_positions(hmds, base_stations):
    
    for hmd in hmds:
        direction = np.random.uniform(0, 2*np.pi)
        dx = np.cos(direction) * 0.1
        dy = np.sin(direction) * 0.1
        x = (hmd.x + dx)
        y = (hmd.y + dy)
        
        
        if x < 0 or x > 1:
            pass
        else:
            hmd.x = x
        
        if y < 0 or y > 1:
            pass
        else:
            hmd.y = y
        
        hmd.connect_to_base_station(base_stations)

# ALREADY IMPLEMENTED! 
def main():
    num_base_stations = 100
    num_hmds = 1
    base_stations = generate_base_stations(num_base_stations, 0.13)
    hmds = generate_hmds(num_hmds, 0.05)
    for hmd in hmds:
        #print(hmd)
        hmd.connect_to_base_station(base_stations)
        #print(hmd)
        #a = input('press to continue')
    
    while True:
        print(f"updating hmds positions")
        update_hmd_positions(hmds, base_stations)
        print(hmds[0].current_base_station.id)
        print_network(base_stations, hmds)
        #time.sleep(0.01)
    

if __name__=="__main__":
    main()
