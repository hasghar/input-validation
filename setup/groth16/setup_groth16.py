import subprocess
import secrets
import os

def run_setup(circuit_name, pow_param):
    """
    Perform the Groth16 trusted setup for a compiled circuit.

    Generates and contributes to a Powers of Tau ceremony, prepares
    the phase 2 parameters, generates the Groth16 proving and
    verification keys, contributes to the phase 2 setup, and exports
    the verification key.

    Args:
        circuit_name (str): Name of the compiled circuit
        pow_param (str): Powers of Tau parameter specifying the
            ceremony size (e.g., "12").

    Returns:
        None
    """
    potname = "pot" + pow_param
    subprocess.run(
        [
            "npx", "snarkjs", "powersoftau", "new",
            "bn128", pow_param,
            os.path.join("outputs", potname + "_0000.ptau"),
        ],
        check=True,
    )

    # Contribute randomness. The command above just uses tau = 1. 
    # Using Python's secrets module to generate randomness instead 
    # of interrupting user
    subprocess.run(
        [
            "npx", "snarkjs", "powersoftau", "contribute",
            os.path.join("outputs", potname + "_0000.ptau"),
            os.path.join("outputs", potname + "_0001.ptau"),
            "--name=randomness contribution",
            "-e=" + secrets.token_hex(32),
        ],
        check=True,
    )

    # Evaluate the polynomials at tau
    subprocess.run(
        [
            "npx", "snarkjs", "powersoftau", "prepare", "phase2",
            os.path.join("outputs", potname + "_0001.ptau"),
            os.path.join("outputs", potname + "_final.ptau"),
        ],
        check=True,
    )

    # Generate a .zkey file that will contain the proving and 
    # verification keys together with all phase 2 contributions
    subprocess.run(
        [
            "npx", "snarkjs", "groth16", "setup",
            os.path.join("outputs", circuit_name + ".r1cs"),
            os.path.join("outputs", potname + "_final.ptau"),
            os.path.join("outputs", circuit_name + "_0000.zkey"),
        ],
        check=True,
    )

    # Contribute to the phase 2 of the ceremony
    subprocess.run(
        [
            "npx", "snarkjs", "zkey", "contribute",
            os.path.join("outputs", circuit_name + "_0000.zkey"),
            os.path.join("outputs", circuit_name + "_final.zkey"),
            "--name=randomness contribution",
            "-e=" + secrets.token_hex(32),
        ],
        check=True,
    )

    # Export the verification key
    subprocess.run(
        [
            "npx", "snarkjs", "zkey", "export", "verificationkey",
            os.path.join("outputs", circuit_name + "_final.zkey"),
            "outputs/verification_key.json", 
        ],
        check=True,
    )

if __name__ == "__main__":
    pow_param = "12"
    circuit_name = "isbinary"
    run_setup(circuit_name, pow_param)
