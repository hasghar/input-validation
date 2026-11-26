import subprocess
import os

def generate_proof(circuit_name):
    """
    Generate a Groth16 zero-knowledge proof for the specified circuit.

    Uses the circuit's proving key and the previously generated witness
    to create a proof and its associated public inputs. Saves the proof
    to outputs/proof.json and the public inputs to outputs/public.json.

    Args:
        circuit_name (str): Name of the circuit, without the .circom
            extension.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If proof generation fails.
    """
    subprocess.run(
        [
            "npx", "snarkjs", "groth16", "prove",
            os.path.join("outputs", circuit_name + "_final.zkey"),
            "outputs/witness.wtns",
            "outputs/proof.json",
            "outputs/public.json",
        ],
        check=True,
    )

    print("Proof generated successfully!")

if __name__ == "__main__":
    circuit_name = "isbinary"
    generate_proof(circuit_name)