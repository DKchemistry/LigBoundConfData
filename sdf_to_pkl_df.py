import os
import argparse
import multiprocessing
import pandas as pd
from rdkit import Chem


def print_help():
    """
    Prints the usage of the script.
    """
    print(
        """
    Converts SDF files to a dataframe with activity status ['Activity'] and rdkit mol objects ['Mol'] using multiprocessing, saves the dataframe to a pickle file.
    
    Usage: python sdf_to_pkl_df.py -a [active_status] -i [input] -o [output] -c [cpus]

    -a, --active_status: The activity status of the molecules. Choices are 'active' or 'inactive'. This is a required argument.
    -i, --input: The SDF files to load. Multiple files can be specified. This is a required argument.
    -o, --output: The output file name. This is a required argument.
    -c, --cpus: The number of CPUs to use. If not specified, all available CPUs will be used. This is an optional argument.

    Example: python sdf_to_pkl_df.py -a active -i file1.sdf file2.sdf -o output.pkl -c 4

    -i can also accept wildcards, like if you have a directory with multiple SDF files, you can do something like this:

    python sdf_to_pkl_df.py -a active -i *.sdf -o output.pkl

    """
    )


def load_sdf_to_dataframe(args):
    """
    Load molecules and their properties from an SDF file into a DataFrame.
    """
    file, active_status = args  # Unpack the tuple of arguments

    # Create a molecule supplier
    mol_supplier = Chem.SDMolSupplier(file)

    # Load the molecules and their properties into a list
    molecules = []
    for mol in mol_supplier:
        if mol is not None:
            props = mol.GetPropsAsDict()
            props["Title"] = mol.GetProp("_Name")
            props["Mol"] = mol
            props["Activity"] = 1 if active_status == "active" else 0
            molecules.append(props)

    # Convert the list into a DataFrame
    df = pd.DataFrame(molecules)

    # Reorder the DataFrame columns
    cols = ["Title", "Mol", "Activity"] + [
        col for col in df.columns if col not in ["Title", "Mol", "Activity"]
    ]
    df = df[cols]

    return df


class CustomHelpAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
    ):
        super(CustomHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        print_help()
        parser.exit()


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Load molecules from SDF files into a DataFrame",
        add_help=False,  # Disable the default help so that we can use our custom one
    )

    # Add the arguments
    parser.add_argument(
        "-a",
        "--active_status",
        type=str,
        choices=["active", "inactive"],
        required=True,
        help="The activity status of the molecules",
    )
    parser.add_argument(
        "-i",
        "--input",
        metavar="F",
        type=str,
        nargs="+",
        required=True,
        help="The SDF files to load",
    )
    parser.add_argument(
        "-h", "--help", action=CustomHelpAction, help="Show this help message and exit"
    )
    parser.add_argument("-o", "--output", required=True, help="The output file name")
    parser.add_argument(
        "-c",
        "--cpus",
        type=int,
        default=multiprocessing.cpu_count(),
        help="The number of CPUs to use",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Check if the output file already exists
    if os.path.exists(args.output):
        print(f"Error: The file {args.output} already exists.")
        return

    # Create a list of tuples for the multiprocessing pool
    files = [(file, args.active_status) for file in args.input]

    # Create a multiprocessing pool
    with multiprocessing.Pool(args.cpus) as pool:
        # Load and convert each SDF file in parallel
        dfs = pool.map(load_sdf_to_dataframe, files)

    # Concatenate the resulting DataFrames
    df = pd.concat(dfs)

    # Save the final DataFrame to a pickle file
    df.to_pickle(args.output)


if __name__ == "__main__":
    main()
