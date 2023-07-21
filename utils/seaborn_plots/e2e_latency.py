import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



df = pd.read_csv(r'/Users/alisson-cds/Downloads/merged_file.csv')

columns = ['net_latency', 'e2e_latency', ]
labels = ['Network latency', 'E2E latency', ]

# Create the violin plot
#plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

# Create a figure with three subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=False)

hue_order = ["alg1", "alg2", "alg3"]

for i in range(3):
    ax = axes[i]
    v = sns.violinplot(x='scenario', y=columns[i], hue='algorithm', hue_order=hue_order, data=df, split=False, inner="quart", linewidth=1,ax=ax)
    ax.set_title(labels[i], fontdict={'size': 10})
    ax.set_xlabel('')
    ax.set_ylabel('FPS')
    ax.legend().remove()  # Remove individual legends from subplots
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    # Add a vertical line to separate scenarios
    for i in range(1, len(df['scenario'].unique())):
        ax.axvline(i - 0.5, color='black', linestyle='dotted', linewidth=0.7)

# Set the title and labels
#plt.title('Test', fontdict={'size': 10})
#plt.xlabel('')
#plt.ylabel('FPS')
#plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

xticks = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]
v.set_xticklabels(xticks)


# Modify the legend labels
handles, labels = v.get_legend_handles_labels()
new_labels = ['Algorithm 1', 'Algorithm 2', 'Algorithm 3']  # Specify the desired legend labels
legend = plt.legend(handles, new_labels, title='', bbox_to_anchor=(-0.8, -0.08), loc='upper center', ncol=3)
legend.get_title().set_fontsize('10')  # Set the legend title font size
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to make space for the legend

plt.subplots_adjust(wspace=0.3)
#plt.savefig("/Users/alisson-cds/Downloads/plots/violin_plot.pdf", format="pdf", bbox_inches='tight')
plt.show()

