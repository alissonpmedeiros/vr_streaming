import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the data for the heatmap
df_heatmap = pd.read_csv('/Users/alisson-cds/Downloads/merged_file.csv')

# Compute aggregated data for the heatmap
agg_data = df_heatmap.groupby(['scenario', 'algorithm'])['net_congested_level'].mean().reset_index()

# Create a pivot table to reshape the data for the heatmap
heatmap_data = agg_data.pivot(index='scenario', columns='algorithm', values='net_congested_level')

# Create a figure with four subplots
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Plot the heatmap in the first subplot
ax_heatmap = axes[0, 0]
h = sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', cbar=True, linewidths=0.5, ax=ax_heatmap)
ax_heatmap.set_title('Network Congestion Levels', fontdict={'size': 10})
ax_heatmap.set_xlabel('')
ax_heatmap.set_ylabel('')
new_xtick_labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]
new_ytick_labels = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]
h.set_xticklabels(new_xtick_labels)
h.set_yticklabels(new_ytick_labels)

# Read the data for the violin plots
df_violin = pd.read_csv('/Users/alisson-cds/Downloads/merged_files2.csv')

columns = ['net_latency', 'allocated_bw', 'average_fps']
labels = ['Average Network Latency', 'Average HMD Bandwidth Allocation', 'Average FPS']
ylabels = ['Latency (ms)', 'Bandwidth (Mbps)', 'FPS']

hue_order = ["alg1", "alg2", "alg3"]

# Plot the violin plots in the remaining subplots
for i in range(3):
    row = i // 2 + 1
    col = i % 2
    ax_violin = axes[row, col]
    v = sns.violinplot(x='scenario', y=columns[i], hue='algorithm', hue_order=hue_order, data=df_violin,
                       split=False, inner="quart", linewidth=1, ax=ax_violin)
    ax_violin.set_title(labels[i], fontdict={'size': 10})
    ax_violin.set_xlabel('')
    ax_violin.set_ylabel(ylabels[i])
    if i == 0:
        handles, _ = ax_violin.get_legend_handles_labels()
    else:
        ax_violin.get_legend().remove()
    ax_violin.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    for j in range(1, len(df_violin['scenario'].unique())):
        ax_violin.axvline(j - 0.5, color='black', linestyle='dotted', linewidth=0.7)

    xticks = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]
    ax_violin.set_xticklabels(xticks)

# Add the legend for the violin plots
legend_ax = axes[0, 1]
legend_ax.legend(handles, hue_order, title='', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=3)
legend_ax.axis('off')

# Adjust the spacing between subplots
plt.subplots_adjust(hspace=0.3, wspace=0.3)

# Save the figure
plt.savefig("/Users/alisson-cds/Downloads/plots/heatmap_and_violin_plots.pdf", format="pdf", bbox_inches='tight')

# Show the figure
plt.show()
