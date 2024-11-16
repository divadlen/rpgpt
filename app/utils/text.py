import re
import numpy as np

def normalize_string(string:str) -> str:
    return re.sub(r'[\s\-_]+', '_', string.lower())


def convert_to_string(value):
    """Convert any non-string values to string, including NaN."""
    if isinstance(value, float) and np.isnan(value):
        return "NaN"  # Convert NaN to the string "NaN"
    return str(value)  # Convert other values to string


def preprocess_data(data):
    """
    Recursively convert lists and other structures to string-safe values.
    Example:
    
    >>> preprocess_data([1, 2, np.nan])
    [1, 2, 'NaN']

    >>> preprocess_data({'a': 1, 'b': np.nan})
    {'a': 1, 'b': 'NaN'}
    """
    if isinstance(data, list):
        return [convert_to_string(val) for val in data]
    elif isinstance(data, dict):
        return {key: preprocess_data(value) for key, value in data.items()}
    else:
        return convert_to_string(data)


def infer_sector_rows(df, selected_sector_codes):
    """
    Infer sector rows based on the selected sector codes.
    Example: 
    
    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    selected_sector_codes : list of str
        The list of sector codes to match.
    
    Returns
    -------
    pd.DataFrame
    """
    alias_mapping = {
        'FB': 'FB',
        'FBT': 'FB',
        'AC': 'AC',
        'CE': 'CE',
    }

    def normalize_codes(codes):
        return [alias_mapping.get(code, code) for code in codes]
    
    def sector_row_match(row_sectors):
        # Handle "wild card" rows
        if "All sectors" in row_sectors:
            return True

        # Exclude rows with 'except' clauses that contain selected sectors
        if "except" in row_sectors:
            # Split out the excluded sectors in 'All (except X, Y, Z)' format
            exclusion_part = row_sectors.split("except")[1].strip("() ")
            excluded_codes = set(normalize_codes([code.strip().replace("and ", "") for code in exclusion_part.split(',')]))

            if any(code in excluded_codes for code in selected_sector_codes):
                return False

        # Split row sectors and check for any overlap with selected codes
        row_codes = set(normalize_codes([code.strip() for code in row_sectors.split(',')]))
        return bool(row_codes.intersection(selected_sector_codes))
    
    # Apply the match function across the Sector column
    selected_sector_codes = normalize_codes(selected_sector_codes)
    matched_df = df[df['sector'].apply(sector_row_match)]
    return matched_df

