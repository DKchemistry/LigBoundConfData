#!/bin/bash

print_help() {
    echo "Usage: $0 -i INPUT_DIR"
    echo
    echo "Run a refactor_Torsion_strain.py script on each file in parallel."
    echo
    echo "Options:"
    echo "  -i, --input INPUT_DIR   The directory of the input files."
    echo "  -h, --help              Show this help message and exit."
}

while (( "$#" )); do
    case "$1" in
        -i|--input)
            input_dir=$2
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

if [[ -z "$input_dir" ]]; then
    echo "Error: Missing required argument"
    print_help
    exit 1
fi

# Activate the Python environment
eval "$(conda shell.bash hook)"
conda activate analytics_env

# Define a function to process a single file
process_file() {
    input_file=$1
    output_file="${input_file%.sdf}.csv"
    python refactor_Torsion_Strain.py -i "$input_file" -o "$output_file"
}

# Export the function so it can be used by parallel
export -f process_file

# Find all .sdf files in the input directory and process them in parallel
find "$input_dir" -name '*.sdf' | parallel process_file