
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv(r'/Users/alisson-cds/Downloads/merged_file.csv')


agg_data = df.groupby(['scenario', 'algorithm'])['net_congested_level'].mean().reset_index()

# Create a pivot table to reshape the data for heatmap
heatmap_data = agg_data.pivot(index='scenario', columns='algorithm', values='net_congested_level')
# Set up the heatmap plot
plt.figure(figsize=(12, 8))
h = sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', cbar=True, linewidths=0.5)
h.get_figure().gca().set_title("")
plt.title('Network Congestion Levels', fontdict={'size': 10})
plt.xlabel('')
plt.ylabel('')

#h.collections[0].colorbar.set_label("New Label")
new_xtick_labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]
new_ytick_labels = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]
h.set_xticklabels(new_xtick_labels)  
h.set_yticklabels(new_ytick_labels)  


#plt.savefig("/Users/alisson-cds/Downloads/plots/plot2.pdf", format="pdf")
plt.show()

