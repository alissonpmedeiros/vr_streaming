import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
data = pd.read_csv('merged.csv')

# List of unique routing algorithms
routing_algorithms = data['routing_algorithm'].unique()


columns = ['flow_latency', 'route_latency', 'overp_net_latency', 'net_congestion', 'fow_throughput', 'fps', 'impaired_services']
# columns = ['net_congestion', 'fow_throughput', 'fps', 'impaired_services']

# Create a figure with three subplots
fig, axes = plt.subplots(nrows=1, ncols=len(columns), figsize=(15, 5))

# Loop through each latency type and create a bar plot for each
for idx, latency_type in enumerate(columns):
    sns.barplot(x='routing_algorithm', y=latency_type, data=data, ax=axes[idx])
    axes[idx].set_title(f'{latency_type}')
    axes[idx].set_xlabel('Routing Algorithm')
    axes[idx].set_ylabel('Latency (ms)')

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
