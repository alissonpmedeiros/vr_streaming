#!/bin/bash

radius_values=("0.12" "0.13" "0.14" "0.15" "0.16" "0.17" "0.18" "0.19" "0.20") # BERN
# radius_values=("0.09" "0.10" "0.11" "0.12" "0.13" "0.14" "0.15" "0.16" "0.17") # GENEVA



# Array to store the process IDs for all scripts
declare -a pids=()

# Function to handle script termination
function cleanup() {
    echo "Stopping Python scripts..."
    for pid in "${pids[@]}"; do
        kill "$pid"
    done
}

# Register cleanup function to handle Ctrl+C and script exit
trap cleanup INT EXIT

for radius in "${radius_values[@]}"; do
    # Execute Python scripts with arguments and store their process IDs
    python3 main.py flatwise "$radius" &
    pids+=($!)
    echo "Running FLATWISE script with radius $radius..."

    python3 main.py swp "$radius" &
    pids+=($!)
    echo "Running SWP script with radius $radius..."

    python3 main.py wsp "$radius" &
    pids+=($!)
    echo "Running WSP script with radius $radius..."
done

# Wait for all scripts to finish
for pid in "${pids[@]}"; do
    wait "$pid"
done

echo "All scripts finished."












# # Function to handle script termination
# function cleanup() {
#     echo "Stopping Python scripts..."
#     kill "${pids[@]}"
# }

# # Register cleanup function to handle Ctrl+C and script exit
# trap cleanup INT EXIT

# # Array to store the process IDs for all scripts
# declare -a pids=()

# for radius in "${radius_values[@]}"; do
#     # Execute Python scripts with arguments and store their process IDs
#     python3 main.py flatwise "$radius" &
#     pids+=($!)
#     echo "Running FLATWISE script with radius $radius..."

#     python3 main.py swp "$radius" &
#     pids+=($!)
#     echo "Running SWP script with radius $radius..."

#     python3 main.py wsp "$radius" &
#     pids+=($!)
#     echo "Running WSP script with radius $radius..."
# done

# # Wait for all scripts to finish
# for pid in "${pids[@]}"; do
#     wait "$pid"
# done

# echo "All scripts finished."
