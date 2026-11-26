from setup.groth16 import compile_circuit
from proving import witness, proof_groth16
from setup.groth16 import setup_groth16
from verification import verify_groth16, verify_kzg
from data import data_extractor
from inputs import generate_input
from setup.kzg import setup_kzg
import os
import json
import config

def run_zkp(circuit_name, newSetup = False):
    """
    Runs the complete zero-knowledge proof (ZKP) for a given circuit.

    If newSetup is True, compiles the circuit and performs the Groth16 setup.
    Otherwise, uses the existing compiled circuit and setup files.

    The workflow consists of:
        1. Compile the circuit (if newSetup is True).
        2. Perform Groth16 setup (if newSetup is True).
        3. Generate the witness.
        4. Generate the Groth16 proof.
        5. Verify the Groth16 proof.

    Args:
        circuit_name (str): Name of the circuit to execute.
        newSetup (bool, optional): Whether to compile the circuit and perform
            a new Groth16 setup. Defaults to False.
    """
    if newSetup:
        run_zkp_setup(circuit_name)

    # Generate witness (JSON file for input) and Groth16 Proof
    run_zkp_proof(circuit_name)

    # Verify Groth16 Proof
    run_zkp_verification()

def run_zkp_setup(circuit_name):
    """
    Runs the setup of zero-knowledge proof (ZKP) for a given circuit.

    It compiles the circuit and performs the Groth16 setup.

    The workflow consists of:
        1. Compile the circuit (if newSetup is True).
        2. Perform Groth16 setup (if newSetup is True).

    Args:
        circuit_name (str): Name of the circuit to execute.
    """
    # Compile the circuit
    pow_param = compile_circuit.compile(circuit_name)

    # Run Groth16 Setup
    setup_groth16.run_setup(circuit_name, pow_param)

def run_zkp_proof(circuit_name):
    """
    Constructs the zero-knowledge proof (ZKP) for a given circuit.

    Uses the existing compiled circuit and setup files.

    The workflow consists of:
        1. Generate the witness.
        2. Generate the Groth16 proof.

    Args:
        circuit_name (str): Name of the circuit to execute.
    """
    # Generate witness (JSON file for input)
    witness.generate_witness(circuit_name)

    # Generate Groth16 Proof
    proof_groth16.generate_proof(circuit_name)

def run_zkp_verification():
    """
    Verifies the zero-knowledge proof (ZKP) for a given circuit.

    Uses the existing compiled circuit and setup files.

    The workflow consists of:
        1. Verify the Groth16 proof.

    Args:
        circuit_name (str): Name of the circuit to execute.
    """
    # Verify Groth16 Proof
    verify_groth16.verify_proof()

def sim_decision(row, col_names, com_in, com_mem):
    """Simulate the server-side decision by verifying the client's input and
    membership commitments against commitments recomputed from the row data.

    Extracts and packs the row attributes into input and membership vectors,
    computes their KZG commitments, and compares them with the supplied
    commitments to determine whether to accept or reject the input.

    Args:
        row: The data row to be processed.
        col_names: Column names corresponding to the row attributes.
        com_in: Client-provided input commitment.
        com_mem: Client-provided membership commitment.

    Returns:
        bool: True if both commitments match (accept), False otherwise (reject).
         False otherwise.
    """
    data_dict = data_extractor.circomify(row, col_names)
    email = data_dict['email_address']
    email1, email2 = data_extractor.packascii40(email)
    email_length = data_dict['email_address_length']
    password = data_dict['password']
    password_packed = data_extractor.packascii20(password)
    password_length = data_dict['password_length']
    r_mem = data_dict['r_mem']
    row_mem = [
        email1, 
        email2, 
        email_length, 
        password_packed, 
        password_length, 
        r_mem
    ]
    
    first_name = data_dict['first_name']
    first_name_packed = data_extractor.packascii20(first_name)
    first_name_length = data_dict['first_name_length']

    last_name = data_dict['last_name']
    last_name_packed = data_extractor.packascii20(last_name)
    last_name_length = data_dict['last_name_length']

    age = data_dict['age']
    sex = data_dict['sex'] 
    education = data_dict['education']
    marital_status = data_dict['marital_status']

    r_in = data_dict['r_in']

    row_in = [
        email1, 
        email2, 
        email_length, 
        password_packed, 
        password_length, 
        first_name_packed, 
        first_name_length,
        last_name_packed,
        last_name_length,
        age,
        sex,
        education,
        marital_status,
        r_in
    ]

    com_in_v = setup_kzg.computeCommitment(row_in)
    com_mem_v = setup_kzg.computeCommitment(row_mem)
    print("com_in == com_in_v:", com_in == com_in_v)
    print("com_mem == com_mem_v:", com_mem == com_mem_v)
    if com_in == com_in_v and com_mem == com_mem_v:
        print("Server decision is accept!")
        return True
    else:
        print("Server decision is reject!")
        return False

def create_input(col_names, dataset, index, comms_data):
    """
    Generate an input for a selected dataset record with commitment randomness.
    This will be used by the ZKP circuit.

    Args:
        col_names: Names of the dataset columns to include.
        dataset: Path to the input CSV dataset.
        anchor: Column used to identify the record.
        index: Zero-based index of the selected record.
        comms_data: Path to the CSV file containing membership commitments.

    Returns:
        None. Saves the generated input as a JSON file.
    """
    row = data_extractor.get_row_by_index(dataset, col_names, index)
    col_names = row.columns.tolist()
    row = row.iloc[0]
    data_dict = data_extractor.circomify(row, col_names)
    # Get the randomness for input commitment
    r_in = generate_input.random_field_element()
    data_dict["r_in"] = r_in
    r_mem = data_extractor.extract_r_mem_by_index(index, comms_data)
    data_dict["r_mem"] = r_mem
    generate_input.createJson(data_dict)

def create_input_and_return_vals(col_names, dataset, index, comms_data):
    """
    Generate an input for a selected dataset record with commitment randomness.
    This will be used by the ZKP circuit.

    Retrieves the selected dataset record, converts its attributes into
    the format expected by the Circom circuit, generates randomness for
    the input commitment, and retrieves the randomness associated with
    the membership commitment. Saves the resulting circuit input as a
    JSON file and returns the updated dataset record.

    Args:
        col_names: The names of the columns.
        dataset: Path to the input CSV dataset.
        index: Zero-based index of the selected record.
        comms_data: Path to the CSV file containing membership commitments.

    Returns:
        pandas.Series: The selected dataset record with input and membership
            commitment randomness added.
    """
    row = data_extractor.get_row_by_index(dataset, col_names, index)
    row = row.iloc[0]
    data_dict = data_extractor.circomify(row, col_names)
    # Get the randomness for input commitment
    r_in = generate_input.random_field_element()
    data_dict["r_in"] = r_in
    r_mem = data_extractor.extract_r_mem_by_index(index, comms_data)
    data_dict["r_mem"] = r_mem
    r_in = data_dict["r_in"]    
    r_mem = data_dict["r_mem"]
    row["r_in"] = r_in
    row["r_mem"] = r_mem
    generate_input.createJson(data_dict)
    return row

def create_random_input(col_names, dataset, anchor, comms_data):
    """
    Generate a random user input with the corresponding membership randomness.

    Args:
        col_names: List of names of the dataset columns to include.
        dataset: Path to the input CSV dataset.
        anchor: Column used to identify the selected record, e.g., email_address
        comms_data: Path to the CSV file containing membership commitments.

    Returns:
        None. Saves the generated input as a JSON file.
    """
    row = data_extractor.get_random_rows(dataset, col_names, n = 1)
    col_names = row.columns.tolist()
    row = row.iloc[0]
    data_dict = data_extractor.circomify(row, col_names)
    # Get the randomness for input commitment
    r_in = generate_input.random_field_element()
    data_dict["r_in"] = r_in
    anchor_val = row[anchor]
    r_mem = data_extractor.extract_r_mem(anchor, anchor_val, comms_data)
    data_dict["r_mem"] = r_mem
    generate_input.createJson(data_dict)

def run_kzg_setup(comms_data, N, D, fast_mode = True):
    """
    Generate the KZG setup parameters for polynomial commitments
    associated with the dataset.

    Args:
        comms_data: Dataset containing the membership commitments.
        N (int): Number of commitments to include in the setup.
        D (int): Maximum polynomial degree for the KZG SRS.
        fast_mode (bool): If True, use optimized field initialization settings
            to skip primality verification and primitive-element search.
            If False, use the default Galois group initialization.

    Returns:
        tuple:
            tau: Random evaluation point used in the setup.
            q_tau_G1: Evaluation of the q polynomial at tau, represented
                as a G1 curve point.
            w_tau_G2s: Evaluations of the w polynomials at tau,
                represented as G2 curve points.
            srs_kzg: KZG structured reference string (SRS).
    """
    tau, q_tau_G1, w_tau_G2s, srs_kzg = setup_kzg.run_setup(comms_data, N, D, fast_mode)
    return tau, q_tau_G1, w_tau_G2s, srs_kzg

def run_kzg_verification(q_tau_G1, srs_kzg, w_tau_G2):
    """
    Verifies a KZG membership.

    Extracts the commitment from the public input JSON file and verifies
    its membership using the provided KZG commitment, SRS, and witness.

    Args:
        q_tau_G1: KZG commitment polynomial q evaluated at tau as a G1 point.
        srs_kzg: KZG structured reference string.
        w_tau_G2: KZG witness polynomial w evaluated at tau as a G2 point.

    Returns:
        bool: Whether the KZG membership proof is valid.
    """
    c = verify_kzg.extract_com_mem_from_json(config.PUBLIC_JSON)
    result = verify_kzg.verify_membership(q_tau_G1, srs_kzg, w_tau_G2, c)
    return result

def extract_inputs(col_names, dataset, n = 1):
    rows = data_extractor.get_rows(dataset, col_names, n)
    print(rows)
    data = data_extractor.circomifyrows(rows)
    return data

def computeHash(data):
    col_names, data = data_extractor.makePoseidonFriendly(data)
    print(col_names)
    print(data)
    pos_hash = setup_kzg.computeCommitment(data[0])
    print(pos_hash)

def sanityCheck(public_data):
    with open(public_data, "r") as f:
        data = json.load(f)

    second_element = int(data[1])
    remaining_elements = [int(x) for x in data[2:]]
    pos_hash = setup_kzg.computeCommitment(remaining_elements)
    print("Poseidon hash from circom:", second_element)
    print("Poseidon hash recalculated:", pos_hash)

if __name__ == "__main__":
    # Toggle if you want to create a new random JSON INPUT with all fields
    createNewInput = True
    # Toggle if new constraints are added. Otherwise proceed to witness generation
    newZKPSetup = True
    # Toggle if you want to run ZKP part
    runZKP = True
    dataset = config.USER_DATA
    comms_data = config.COMMS_DATA
    index = 3
    if createNewInput:
        col_names = ["email_address", "password", "first_name", "last_name", "age", "sex", "education", "marital_status"]
        create_input(col_names, dataset, index, comms_data)
    if runZKP:
        circuit_name = config.CIRCUIT_NAME
        run_zkp(circuit_name, newZKPSetup)
