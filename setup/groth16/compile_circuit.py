import subprocess
import os

def compile(circuit_name):
    """
    Compile a Circom circuit and determine the required Powers of Tau
    parameter based on its number of constraints.

    Checks and prints the Circom version, compiles the specified circuit
    to generate its R1CS, WASM, and symbol files, and retrieves the
    number of constraints using snarkjs.

    Args:
        circuit_name (str): Name of the Circom circuit, without the
            .circom extension.

    Returns:
        str: Powers of Tau parameter required for the circuit, calculated
            as the bit length of the number of constraints.

    Raises:
        subprocess.CalledProcessError: If Circom compilation or snarkjs
            execution fails.
        RuntimeError: If the number of constraints cannot be extracted
            from the snarkjs output.
    """
    result = subprocess.run(
        ["circom", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )

    print("Circom version:", result.stdout.strip())

    subprocess.run(
        [
            "circom",
            os.path.join("circuits", circuit_name + ".circom"),
            "--r1cs",
            "--wasm",
            "--sym",
            "-l",
            "node_modules",
            "-o",
            "outputs",
        ],
        check=True,
    )

    print("Compilation successful!")

    # Checking number of constraints
    result = subprocess.run(
        ["npx", "snarkjs", "r1cs", "info", os.path.join("outputs", circuit_name + ".r1cs")],
        capture_output=True,
        text=True,
        check=True
    )

    print(result.stdout)

    try:
        constraints = int(result.stdout.split("# of Constraints:")[1].split()[0])
        pow_param = str(constraints.bit_length())

    except (IndexError, ValueError):
        raise RuntimeError("Could not extract number of constraints from snarkjs output")

    print(f"Total constraints: {constraints}")
    print(f"Required Powers of Tau: {pow_param}")
    return pow_param



if __name__ == "__main__":
    circuit_name = "isbinary"
    compile(circuit_name)