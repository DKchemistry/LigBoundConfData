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
