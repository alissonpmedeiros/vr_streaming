import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file
data = pd.read_csv('merged_file.csv')

# Define the columns to include in the plots
columns_to_include = ['standard_8k', 'standard_4k', 'standard_2k', 'standard_1k',
                      'high_8k', 'high_4k', 'high_2k', 'high_1k']

# Set up the figure and axis for the subplots
fig, axs = plt.subplots(1, 4, figsize=(15, 4))

# Generate the subplots for each scenario
for scenario, ax in zip(range(1, 5), axs.flatten()):
    # Filter the data for the current scenario
    scenario_data = data[data['scenario'] == f'scenario {scenario}']

    # Generate the barplot
    sns.barplot(x='algorithm', y='value', hue='variable', data=pd.melt(scenario_data, id_vars=['algorithm'], value_vars=columns_to_include), ax=ax)

    # Set labels and title
    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Bandwidth')
    ax.set_title(f'Scenario {scenario}')

    # Add a legend
    ax.legend(title='Bandwidth', loc='upper right')

# Adjust the layout and spacing
plt.tight_layout()

# Show the plot
plt.show()
