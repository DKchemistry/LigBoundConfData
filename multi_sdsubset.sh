#!/bin/bash

# Total number of entries in the file
total_entries=531516

# Number of parts to split the file into
parts=10

# Calculate the number of entries per part
entries_per_part=$((total_entries / parts))

# Calculate the ranges for each part
for ((i=0; i<parts; i++))
do
    start=$((i * entries_per_part + 1))
    end=$((start + entries_per_part - 1))

    # Adjust the end for the last part
    if ((i == parts - 1)); then
        end=$total_entries
    fi

    # Print the start and end for each part
    echo "Part $((i+1)): $start-$end"

    # Run the Schrodinger command in parallel
    $SCHRODINGER/utilities/structsubset -n $start-$end 67B3_inactives.sdf subset_$((i+1)).sdf &
done

# Wait for all background jobs to finish
wait