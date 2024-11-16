import json
import numpy as np




def custom_json_decoder(dct:dict) -> dict:
    # Recursively handle the values that might be "NaN" placeholders
    for key, value in dct.items():
        if isinstance(value, str) and value == "NaN":
            dct[key] = np.nan  # Convert "NaN" placeholder back to np.nan
    return dct
