import pandas as pd
import os
import json

COLUMN_TYPES = {
    "first_name": "ascii",
    "last_name": "ascii",
    "email_address": "ascii",
    "password": "ascii",
    "age": "integer",
    "sex": "categorical",
    "education": "categorical",
    "marital_status": "categorical",
    "email_address_length": "integer",
    "password_length": "integer",
    "r_in": "integer",
    "r_mem": "integer"
}

MAX_LENGTHS = {
    "first_name": 20,
    "last_name": 20,
    "password": 20,
    "email_address": 40
}

SEX_MAP = {
    "Male": 0,
    "Female": 1
}

EDUCATION_MAP = {
    "Bachelors": 0,
    "HS-grad": 1,
    "11th": 2,
    "Masters": 3,
    "9th": 4,
    "Some-college": 5,
    "Assoc-acdm": 6,
    "Assoc-voc": 7,
    "7th-8th": 8,
    "Doctorate": 9,
    "Prof-school": 10,
    "5th-6th": 11,
    "10th": 12,
    "1st-4th": 13,
    "Preschool": 14,
    "12th": 15
}

MARITAL_STATUS_MAP = {
    "Never-married": 0,
    "Married-civ-spouse": 1,
    "Divorced": 2,
    "Married-spouse-absent": 3,
    "Separated": 4,
    "Married-AF-spouse": 5,
    "Widowed": 6
}

CATEGORICAL_MAP = {
    "sex": SEX_MAP,
    "education": EDUCATION_MAP,
    "marital_status": MARITAL_STATUS_MAP
}

# See how dataset looks like
def inspect_dataset(dataset, col_name):
    df = pd.read_csv(dataset)
    print("Dataset shape:", df.shape)
    print("Columns:", df.columns)
    nuniquevals = df[col_name].nunique()
    col_type = df[col_name].dtype
    print("Column type:", col_type)
    print("Number of unique values:", nuniquevals)
    # don't bother printing unique vals if they are too many
    if nuniquevals < 20:
        print("Unique values:", df[col_name].unique())
    print(df.head())
    if df[col_name].apply(lambda x: x.isascii() if isinstance(x, str) else True).all():
        print(f"all values in {col_name} are ascii characters")
    if col_type == "int64":
        print("Minimum value:", df[col_name].min())
        print("Maximum value:", df[col_name].max())
    else:
        # does not apply to int64 type columns
        max_length = df[col_name].str.len().max()
        print(f"maximum length of text in {col_name} is {max_length}")

def extract_public_commitments(indexes, json_file):
    """Extract public commitments at the specified indexes from a JSON file.

    Args:
        indexes: List of zero-based indexes of the commitments to extract.
        json_file: Path to the JSON file containing the commitments.

    Returns:
        list[int]: Public commitments at the specified indexes, converted to integers.
    """
    with open(json_file, "r") as f:
        data = json.load(f)
        comms = []
        for index in indexes:
            comms.append(int(data[index]))
    return comms

def get_random_rows(dataset, col_names, n = 1):
    """
    Retrieve n randomly selected rows from specified columns of a CSV dataset.

    Args:
        dataset: Path to the input CSV file.
        col_names: Names of the columns to retrieve.
        n: Number of random rows to retrieve (default: 1).

    Returns:
        DataFrame containing the selected rows and columns.
    """
    df = pd.read_csv(dataset)
    random_rows = df[col_names].sample(n=n)
    return random_rows

def extract_r_mem(anchor, anchor_val, comms_data):
    """
    Retrieve the r_mem value for a record matching the given anchor value.

    Args:
        anchor: Name of the column used to identify the record, e.g., email_address.
        anchor_val: Value to match in the anchor column.
        comms_data: Path to the CSV file containing the commitments.

    Returns:
        The r_mem field value.
    """
    df = pd.read_csv(comms_data)
    r_mem = df.loc[df[anchor] == anchor_val, "r_mem"]
    return r_mem

def extract_r_mem_by_index(index, comms_data):
    """
    Retrieve the r_mem value for a record by its index.

    Args:
        index: Zero-based index of the record.
        comms_data: Path to the CSV file containing the commitments.

    Returns:
        The r_mem field value.

    Raises:
        IndexError: If the index is out of range.
    """
    df = pd.read_csv(comms_data)
    if index < 0 or index >= len(df):
        raise IndexError("Row index out of range")
    return df.iloc[index]["r_mem"]

def get_rows(dataset, col_names, n = 1):
    """
    Read the first n rows of selected columns from a CSV dataset.

    Args:
        dataset: Path to the input CSV file.
        col_names: Names of the columns to retrieve.
        n: Number of rows to retrieve (default: 1).

    Returns:
        DataFrame containing the selected columns and rows.
    """
    df = pd.read_csv(dataset)
    rows = df[col_names].head(n)
    return rows 

def get_row_by_index(dataset, col_names, index):
    """
    Retrieve a row from a CSV dataset by its index.

    Args:
        dataset: Path to the input CSV file.
        col_names: Names of the columns to retrieve.
        index: Zero-based index of the row to retrieve.

    Returns:
        The selected row as a pandas Dataframe.

    Raises:
        IndexError: If the index is out of range.
    """
    df = pd.read_csv(dataset)
    if index < 0 or index >= len(df):
        raise IndexError("Row index out of range")
    row =  df[col_names].iloc[[index]]
    return row

def num_rows(dataset):
    """
    Return the number of rows in a CSV dataset.

    Args:
        dataset: Path to the input CSV file.

    Returns:
        Number of rows in the dataset.
    """
    df = pd.read_csv(dataset)
    return len(df)

# Convert string to an array of ascii codes
# Also return the length
def string_to_ascii(value, col_name):
    """
    Converts a string into a fixed-length array of ASCII values.

    Each character is converted to its ASCII integer representation.
    The resulting array is padded with zeros to match the maximum
    allowed length specified for the column.

    Args:
        value (str): The input string to convert.
        col_name (str): The column name used to determine the maximum
            allowed string length from MAX_LENGTHS.

    Returns:
        tuple: A tuple containing:
            - ascii_array (list[int]): Fixed-length array of ASCII values,
              padded with zeros.
            - length (int): Number of characters in the original string.

    Raises:
        ValueError: If the string contains non-ASCII characters or
            exceeds the maximum allowed length for the column.
    """
    if not value.isascii():
        raise ValueError("String contains non-ASCII characters")

    if len(value) > MAX_LENGTHS[col_name]:
        raise ValueError(f"String {value} exceeds maximum length of {MAX_LENGTHS[col_name]}")

    ascii_array = [ord(char) for char in value]
    length = len(ascii_array)

    ascii_array += [0] * (MAX_LENGTHS[col_name] - length)

    return ascii_array, length

def circomify(row, col_names):
    """
    Converts a data row into a dictionary of values formatted for Circom inputs.
    Strings are converted into an array of ascii values with a length parameter
    showing the number of active characters.

    Each column is processed according to its type, as specified in
    COLUMN_TYPES:
        - "ascii": Converts the string into a fixed-length array of ASCII
          values and adds a corresponding length field.
        - "integer": Converts the value to an integer.
        - "categorical": Maps the value to its corresponding integer
          representation using CATEGORICAL_MAP.

    Args:
        row (dict): Dictionary containing the original data row, with
            column names as keys.
        col_names (list[str]): Names of the columns to include in the
            resulting dictionary.

    Returns:
        dict: Dictionary containing the Circom-compatible input values.

    Raises:
        ValueError: If a categorical column has no defined mapping or
            a column has an unknown type.
    """
    data_dict = {}
    for col_name in col_names:
        value = row[col_name]
        col_type = COLUMN_TYPES[col_name]
        if col_type == "ascii":
            circom_value, circom_length = string_to_ascii(value, col_name)
            data_dict[col_name] = circom_value
            col_length_name = col_name + "_length"
            data_dict[col_length_name] = circom_length
        elif col_type == "integer":
            circom_value = int(value)
            data_dict[col_name] = circom_value
        elif col_type == "categorical":
            mapping = CATEGORICAL_MAP.get(col_name)
            if mapping is not None:
                data_dict[col_name] = mapping[value]
            else:
                raise ValueError(f"No mapping defined for categorical column: {col_name}")
        else:
            raise ValueError(f"Unknown column type for {col_name}")
    return data_dict

def circomifyrows(rows):
    """
    Converts a pandas DataFrame into a list of dictionaries formatted
    for use as Circom inputs.

    Each row is processed using circomify(), which converts values
    according to their corresponding column types.

    Args:
        rows (pandas.DataFrame): DataFrame containing the input records.

    Returns:
        list[dict]: List of dictionaries, where each dictionary contains
            the Circom-compatible values for one row.
    """
    data = []
    col_names = rows.columns.tolist()
    for _, row in rows.iterrows():
        record = circomify(row, col_names)
        data.append(record)
    return data

def packascii20(ascii_array):
    """
    Packs an array of 20 ASCII values into a single integer.

    Each ASCII value is represented using 7 bits (base 128). The
    characters are packed into a single integer, with the character
    at index i contributing ascii_array[i] * 128^i.

    Args:
        ascii_array (list[int]): Array of 20 ASCII values (0–127).

    Returns:
        int: Integer representing the packed ASCII array.
    """
    packed = 0
    power = 1
    for i in range(20):
        packed = packed + ascii_array[i] * power
        power *= 128
    return packed

def packascii40(ascii_array):
    """
    Packs an array of 40 ASCII values into two integers.

    Each ASCII value is represented using 7 bits (base 128).
    The first 36 characters are packed into the first integer,
    and the remaining 4 characters are packed into the second integer.
    The character at index i within each segment contributes
    ascii_array[i] * 128^i. 

    This is to ensure that each packed integer fits into the field
    F_p where p is as in the BN254 scalar field.

    Args:
        ascii_array (list[int]): Array of 40 ASCII values (0–127).

    Returns:
        tuple[int, int]: Two integers representing the packed ASCII
            array, with the first 36 characters in the first integer
            and the remaining 4 characters in the second integer.
    """
    packed1 = 0
    packed2 = 0
    power = 1
    for i in range(36):
        packed1 = packed1 + ascii_array[i] * power
        power *= 128

    power = 1
    for i in range(36, 40):
        packed2 = packed2 + ascii_array[i] * power
        power *= 128
    
    return packed1, packed2

def makePoseidonFriendly(data):
    """
    Converts a list of Circom-compatible data records into rows of
    integers suitable for Poseidon hashing.

    ASCII arrays are packed into integers using packascii20() or
    packascii40(), depending on their maximum allowed length.
    Non-ASCII values are appended unchanged.

    Column names are updated to reflect any columns that are split
    into multiple packed integers.

    Args:
        data (list[dict]): List of dictionaries containing Circom-compatible
            input values.

    Returns:
        tuple[list[str], list[list[int]]]:
            - column_names: Names corresponding to the processed columns.
              ASCII columns of maximum length 40 are split into two
              columns with suffixes "_1" and "_2".
            - processed_rows: List of rows containing the packed integer
              representations of the original data.

    Raises:
        ValueError: If an ASCII column has an unsupported maximum length.
    """
    processed_rows = []
    column_names = []

    for row_index, row in enumerate(data):
        prow = []
        for key, value in row.items():
            col_type = COLUMN_TYPES[key]
            if col_type == "ascii":
                max_length = MAX_LENGTHS[key]
                if max_length == 20:
                    prow.append(packascii20(value))
                    if row_index == 0:
                        column_names.append(key)
                elif max_length == 40:
                    packed1, packed2 = packascii40(value)
                    prow.extend([packed1, packed2])
                    if row_index == 0:
                        column_names.extend([key + "_1", key + "_2"])
                else:
                    raise ValueError(f"Unknown maximum length: {max_length}")
            else:
                prow.append(value)
                if row_index == 0:
                    column_names.append(key)
        processed_rows.append(prow)
    return column_names, processed_rows
    
if __name__ == "__main__":
    data_dir = ""
    dataset = os.path.join(data_dir, "augmented_adult.csv")
    col_name = "password"
    inspect_dataset(dataset, col_name)
    #print(get_random_element(dataset, col_name))