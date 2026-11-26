import os

# Project and data directories
DATA_DIR = "/Path/To/datasets"
PROJECT_ROOT = "/Path/To/Project/Root/input-validation"
RESULTS_DIR = "/Path/To/results"
PLOTS_DIR = "/Path/To/plots"

# Datasets
USER_DATA = os.path.join(DATA_DIR, "augmented_adult.csv")
COMMS_DATA = os.path.join(DATA_DIR, "comms_data.csv")

# Project directories
OUTPUTS = os.path.join(PROJECT_ROOT, "outputs")
INPUTS = os.path.join(PROJECT_ROOT, "inputs")

# Groth16 files
PUBLIC_JSON = os.path.join(OUTPUTS, "public.json")
INPUT_JSON = os.path.join(INPUTS, "input.json")
PROOF_JSON = os.path.join(OUTPUTS, "proof.json")

# Global parameters
CIRCUIT_NAME = "validate_fields"