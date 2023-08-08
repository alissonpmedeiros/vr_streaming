import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('/Users/alisson-cds/Downloads/merged_file.csv')

scenario_order = ['scenario 1', 'scenario 2', 'scenario 3', 'scenario 4']
hue_order = ['alg1', 'alg2', 'alg3']
new_labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]

fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

a0 = axes[0, 0]
a1 = axes[0, 1]
a2 = axes[1, 0]
a3 = axes[1, 1]

sns.histplot(data=df[df['scenario'] == 'scenario 1'], x='total_allocate_bw', hue='algorithm', hue_order=hue_order, ax=a0)
sns.histplot(data=df[df['scenario'] == 'scenario 2'], x='total_allocate_bw', hue='algorithm', hue_order=hue_order, ax=a1)
sns.histplot(data=df[df['scenario'] == 'scenario 3'], x='total_allocate_bw', hue='algorithm', hue_order=hue_order, ax=a2)
sns.histplot(data=df[df['scenario'] == 'scenario 4'], x='total_allocate_bw', hue='algorithm', hue_order=hue_order, ax=a3)

a0.set_title("Scenario 1", fontdict={'size': 10})
a1.set_title("Scenario 2", fontdict={'size': 10})
a2.set_title("Scenario 3", fontdict={'size': 10})
a3.set_title("Scenario 4", fontdict={'size': 10})

a0.set_xlabel("Network Bandwidth Allocation (Mbps)", fontdict={'size': 10})
a1.set_xlabel("Network Bandwidth Allocation (Mbps)", fontdict={'size': 10})
a2.set_xlabel("Network Bandwidth Allocation (Mbps)", fontdict={'size': 10})
a3.set_xlabel("Network Bandwidth Allocation (Mbps)", fontdict={'size': 10})

plt.ticklabel_format(axis='x', style='scientific', scilimits=(0, 0))
plt.ticklabel_format(axis='y', style='plain', scilimits=(0, 0))

# Get the handles and labels of the original legend from the first subplot
handles, labels = a0.get_legend_handles_labels()

# Create a dictionary to map the original labels to the new labels
labels_map = dict(zip(labels, new_labels))

# Replace the labels with the new labels
new_labels = [labels_map[l] for l in labels]

# Add the modified legend to the last subplot
a3.legend(handles, new_labels, loc='lower center', bbox_to_anchor=(-1.11, -0.33), ncol=3)

plt.subplots_adjust(bottom=0.22)
plt.show()
