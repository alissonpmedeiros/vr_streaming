import simpy
import random

# Constants
SIMULATION_TIME = 10  # Total simulation time in seconds
FLOW_COUNT = 5  # Total number of flows

# Flow class
class Flow:
    def __init__(self, flow_id):
        self.flow_id = flow_id

# Network process
def network(env, flow):
    #print(f"Flow {flow.flow_id} arrived at time {env.now}")
    yield env.timeout(random.uniform(0, 1))  # Simulate processing time
    print(f"Flow {flow.flow_id} processed at time {env.now}")

# Simulation environment
env = simpy.Environment()

# Generate flows
flows = [Flow(i) for i in range(FLOW_COUNT)]


# Start network processes for each flow
for flow in flows:
    env.process(network(env, flow))

# Run simulation
env.run(until=SIMULATION_TIME)
#print(f'\n\n')
#env.run(until=11)