import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, MaxNLocator

# Read the data for the heatmap
df_heatmap = pd.read_csv('/Users/alisson-cds/Downloads/merged_file.csv')

# Compute aggregated data for the heatmap
agg_data = df_heatmap.groupby(['scenario', 'algorithm'])['net_congested_level'].mean().reset_index()

# Create a pivot table to reshape the data for the heatmap
heatmap_data = agg_data.pivot(index='scenario', columns='algorithm', values='net_congested_level')

# Create a figure with four subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot the heatmap in the first subplot
ax_heatmap = axes[0]
h = sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', cbar=True, linewidths=0.5, ax=ax_heatmap, cbar_kws={'format': '%.0f%%'})
ax_heatmap.set_title('Network Congestion Levels', fontdict={'size': 10})
ax_heatmap.set_xlabel('')
ax_heatmap.set_ylabel('Scenarios')
new_xtick_labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]
new_ytick_heatmap_labels = ["1", "2", "3", "4"]
new_ytick_labels = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]

#h.set_ylabel('Scenarios')
h.set_xticklabels(new_xtick_labels)
h.set_yticklabels(new_ytick_heatmap_labels)
#ax_heatmap.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

# Read the data for the violin plots
df_violin = pd.read_csv('/Users/alisson-cds/Downloads/merged_files2.csv')

columns = ['net_latency', 'average_fps']
labels = ['Average Network Latency', 'Average FPS']
ylabels = ['Latency (ms)', 'FPS']

hue_order = ["alg1", "alg2", "alg3"]

# Plot the violin plots in the remaining subplots
for i in range(2):
    ax_violin = axes[i+1]
    v = sns.violinplot(x='scenario', y=columns[i], hue='algorithm', hue_order=hue_order, data=df_violin,
                       split=False, inner="quart", linewidth=1, ax=ax_violin)
    ax_violin.set_title(labels[i], fontdict={'size': 10})
    ax_violin.set_xlabel('')
    ax_violin.set_ylabel(ylabels[i])
    ax_violin.legend().remove()
    ax_violin.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    
    for j in range(1, len(df_violin['scenario'].unique())):
        ax_violin.axvline(j - 0.5, color='black', linestyle='dotted', linewidth=0.7)

    xticks = new_ytick_labels
    ax_violin.set_xticklabels(xticks)
    #ax_violin.set_xlabel('Scenarios')

# Modify the legend labels
handles, labels = v.get_legend_handles_labels()
print(handles)
print(labels)
new_labels = ['Algorithm 1', 'Algorithm 2', 'Algorithm 3']  # Specify the desired legend labels
legend = plt.legend(handles, new_labels, title='', bbox_to_anchor=(-0.8, -0.08), loc='upper center', ncol=3)
legend.get_title().set_fontsize('10')  # Set the legend title font size
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to make space for the legend

# Adjust the spacing between subplots
plt.subplots_adjust(wspace=0.3)
# Save the figure

plt.savefig("/Users/alisson-cds/Downloads/plots/new_heatmap_and_violin_plots.pdf", format="pdf", bbox_inches='tight')

# Show the figure
#plt.tight_layout()
#plt.show()


