import json
import os
from data import data_extractor
import secrets
from py_ecc.bn128 import curve_order
import config

def createJson(data_dict):
    """
    Creates a JSON input file from the provided dictionary.

    Args:
        data_dict (dict): Dictionary containing the input data to be
            written to the JSON file.

    Writes:
        JSON file to the path specified by config.INPUT_JSON.
    """
    data = data_dict
    with open(config.INPUT_JSON, "w") as f:
        json.dump(data, f, indent=4)
    print("Input JSON created successfully! Check inputs/input.json")

def random_field_element():
    """Generate a cryptographically secure random field element.

    Returns:
        str: A randomly generated integer in the range [0, curve_order - 1],
             represented as a string.
    """
    return str(secrets.randbelow(curve_order))

if __name__ == "__main__":
    data_dict = {
        "x" : 5
    }
    createJson(data_dict)