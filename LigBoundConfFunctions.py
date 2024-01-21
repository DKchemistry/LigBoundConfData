import requests


def get_pfam_data(pdb_id):
    """
    Retrieves Pfam json data for a given PDB ID.

    Args:
        pdb_id (str): The PDB ID for which to retrieve PFAM data.

    Returns:
        dict: A dictionary containing the PFAM data.
    """
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/pfam/{pdb_id}"
    response = requests.get(url)
    data = response.json()
    return data


# Function to extract the first identifier from the JSON data
def get_first_pfam_identifier(pdb_id, json_data):
    """
    Get the 'identifier' (target class) of the first Pfam entry for a given PDB ID.

    Args:
        pdb_id (str): The PDB ID.
        json_data (dict): The JSON data containing Pfam information.

    Returns:
        str or None: The identifier of the first Pfam entry, or None if no Pfam entry exists.
    """
    pfam_data = json_data[pdb_id.lower()]["Pfam"]
    first_pfam_id = next(iter(pfam_data), None)
    return pfam_data[first_pfam_id]["identifier"] if first_pfam_id else None


def add_pfam_identifiers(df):
    """
    Adds Pfam identifiers to the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the protein data.

    Returns:
    pandas.DataFrame: The DataFrame with the added Pfam identifiers.
    """
    # Create a new column 'Pfam_Identifier' in the DataFrame
    df["Pfam_Identifier"] = None

    # Loop through the 'pdb' column in the DataFrame
    for index, row in df.iterrows():
        # Get the PDB ID
        pdb_id = row["PDBid"]
        # Call get_protein_data for the PDB ID
        protein_data = get_pfam_data(pdb_id)
        # Get the identifier
        identifier = get_first_pfam_identifier(pdb_id, protein_data)
        # Add the identifier to the DataFrame
        df.loc[index, "Pfam_Identifier"] = identifier

    return df


def load_sdf_to_dataframe(filename, active):
    """
    Load molecules from an SDF file into a pandas DataFrame. Properties are loaded as well. Activity status is added by user. The DataFrame is ordered by the columns: Title, Mol, Activity, and then the properties.

    Args:
        filename (str): The path to the SDF file.
        active (bool): Flag indicating whether the molecules are active or not.

    Returns:
        pandas.DataFrame: A DataFrame containing the loaded molecules and their properties.
    """
    # Create a molecule supplier
    mol_supplier = Chem.SDMolSupplier(filename)

    # Load the molecules and their properties into a list
    molecules = []
    for mol in mol_supplier:
        if mol is not None:
            props = mol.GetPropsAsDict()
            props["Title"] = mol.GetProp("_Name")
            props["Mol"] = mol
            props["Activity"] = 1 if active else 0
            molecules.append(props)

    # Convert the list into a DataFrame
    df = pd.DataFrame(molecules)

    # Reorder the DataFrame columns
    cols = ["Title", "Mol", "Activity"] + [
        col for col in df.columns if col not in ["Title", "Mol", "Activity"]
    ]
    df = df[cols]

    return df


# Usage:
active = load_sdf_to_dataframe("67B3_actives.sdf", active=True)
inactive = load_sdf_to_dataframe("67B3_inactives.sdf", active=False)
