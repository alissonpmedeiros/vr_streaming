import os
import csv
import paramiko
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def append_matching_lines(file1_path, file2_path, file3_path,output_path):
    # Read the CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    df3 = pd.read_csv(file3_path)

    # Get the number of rows in df1
    num_rows_file1 = len(df1)

    # Take only the first num_rows_file1 rows from df2
    df2_selected = df2[:num_rows_file1]
    df3_selected = df3[:num_rows_file1]

    # Append the selected rows from df2 to df1
    appended_df = pd.concat([df1, df2_selected, df3_selected], ignore_index=True)

    # Save the appended dataframe to a new CSV file
    appended_df.to_csv(output_path, index=False)

def append_csv_files(file1_path, file2_path, output_path):
    # Read the CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    # Append the rows from df2 to df1
    appended_df = df1.append(df2, ignore_index=True)

    # Save the appended dataframe to a new CSV file
    appended_df.to_csv(output_path, index=False)

def merge_csv_files(file1_path, file2_path, output_path):
    # Read the CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path, skiprows=1)  # Skip the header in file2

    # Get the number of rows in file1
    num_rows_file1 = len(df1)

    # Take only the first num_rows_file1 rows from file2
    df2 = df2[:num_rows_file1]

    # Concatenate the dataframes vertically
    merged_df = pd.concat([df1, df2], axis=1)

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(output_path, index=False)


def download_csv_from_remote(remote_host, remote_port, remote_user, private_key_path, remote_csv_path, local_download_path):
    private_key = paramiko.RSAKey(filename=private_key_path)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(remote_host, port=remote_port, username=remote_user, pkey=private_key)
        sftp = ssh.open_sftp()
        sftp.get(remote_csv_path, local_download_path)
        sftp.close()
        ssh.close()
        #print(f"Downloaded remote CSV file from '{remote_csv_path}' to '{local_download_path}'")
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Rest of the script remains unchanged
# ...

# Specify remote host credentials and paths including the private key
remote_host = '130.92.70.8'
remote_port = 2711
remote_user = 'medeiros'
private_key_path = r'/Users/alisson-cds/.ssh/id_rsa'  # Update this
RADIUS = 16

remote_first_csv_path = '/home/medeiros/vr_streaming/results/bern/r_0_{}/wsp.csv'.format(RADIUS)
local_first_csv_path = r'/Users/alisson-cds/Desktop/vr_streaming/utils/plots/new_plots/wsp.csv'

remote_second_csv_path = '/home/medeiros/vr_streaming/results/bern/r_0_{}/flatwise.csv'.format(RADIUS)
local_second_csv_path = r'/Users/alisson-cds/Desktop/vr_streaming/utils/plots/new_plots/flatwise.csv'

remote_third_csv_path = '/home/medeiros/vr_streaming/results/bern/r_0_{}/swp.csv'.format(RADIUS)
local_third_csv_path = r'/Users/alisson-cds/Desktop/vr_streaming/utils/plots/new_plots/swp.csv'

output_csv_path = r'/Users/alisson-cds/Desktop/vr_streaming/utils/plots/new_plots/merged.csv'

download_csv_from_remote(remote_host, remote_port, remote_user, private_key_path, remote_first_csv_path, local_first_csv_path)
download_csv_from_remote(remote_host, remote_port, remote_user, private_key_path, remote_second_csv_path, local_second_csv_path)
download_csv_from_remote(remote_host, remote_port, remote_user, private_key_path, remote_third_csv_path, local_third_csv_path)

append_matching_lines(local_first_csv_path, local_second_csv_path, local_third_csv_path,output_csv_path)

#a = input('type to continue...')

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
    axes[idx].set_xlabel('')
    # axes[idx].set_ylabel('Latency (ms)')

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
