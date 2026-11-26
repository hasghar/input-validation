import os
import subprocess

def generate_witness(circuit_name):
    """
    Generate a witness for the specified compiled Circom circuit.

    Executes the generated JavaScript witness generator using the circuit's
    WASM file and the input data provided in inputs/input.json. Saves the
    resulting witness to outputs/witness.wtns.

    Args:
        circuit_name (str): Name of the compiled circuit, without the
            .circom extension.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If witness generation fails.
    """
    dir_js = circuit_name + "_js"
    subprocess.run(
        [
            "node",
            os.path.join("outputs", dir_js, "generate_witness.js"),
            os.path.join("outputs", dir_js, circuit_name + ".wasm"),
            "inputs/input.json",
            "outputs/witness.wtns",
        ],
        check=True,
    )

    print("Witness generated successfully!")

if __name__ == "__main__":
    circuit_name = "isbinary"
    generate_witness(circuit_name)