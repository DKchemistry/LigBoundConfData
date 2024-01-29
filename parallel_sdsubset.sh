#!/bin/bash

# Define a function to print the help message
print_help() {
    echo "Usage: $0 -f FILE -p PARTS -c CPUS -o OUTPUT"
    echo
    echo "Split (sdsubtruct) an sdf into roughly equally sized parts using 'parallel'."
    echo
    echo "Options:"
    echo "  -f, --file FILE    The file to split."
    echo "  -p, --parts PARTS  The number of parts to split the file into."
    echo "  -c, --cpus CPUS    The number of CPUs to use."
    echo "  -o, --output OUTPUT The prefix for the output files."
    echo "  -h, --help         Show this help message and exit."
}

# Parse the command-line arguments
while (( "$#" )); do
    case "$1" in
        -f|--file)
            file=$2
            shift 2
            ;;
        -p|--parts)
            parts=$2
            shift 2
            ;;
        -c|--cpus)
            cpus=$2
            shift 2
            ;;
        -o|--output)
            output=$2
            shift 2
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo "Error: Invalid argument"
            print_help
            exit 1
            ;;
    esac
done


# Check that all required arguments were provided
if [[ -z "$file" || -z "$parts" || -z "$cpus" || -z "$output" ]]; then
    echo "Error: Missing required argument"
    print_help
    exit 1
fi

# Create the output directory if it does not exist
output_dir=$(dirname "$output")
mkdir -p "$output_dir"

# Calculate the number of entries in the file
total_entries=$(grep -c '$$$$' "$file")

# Calculate the number of entries per part
entries_per_part=$((total_entries / parts))

# Calculate the remainder
remainder=$((total_entries % parts))

# Export variables for use in parallel
export entries_per_part remainder parts file output

# Run the tasks in parallel
seq 0 $((parts-1)) | parallel -j $cpus '
    i={}
    start=$((i * entries_per_part + 1))
    end=$((start + entries_per_part - 1))

    # Add the remainder to the last part
    if ((i == parts - 1)); then
        end=$((end + remainder))
    fi

    # Print the start and end for each part
    echo "Part $((i+1)): $start-$end"

    # Run the Schrodinger command
    $SCHRODINGER/utilities/structsubset -n $start-$end "$file" "${output}_subset_$((i+1)).sdf"
'