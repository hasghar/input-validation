import benchmark 
import config
import os
from setup.kzg import setup_kzg
from data import data_extractor
from main import (
    run_zkp_setup, 
    run_kzg_setup, 
    run_zkp_proof, 
    run_zkp_verification, 
    run_kzg_verification, 
    create_input,
    create_input_and_return_vals,
    sim_decision
)

def benchmark_zkp_setup(zkp_setup_results_file, runs):
    """
    Benchmarks Groth16 setup over multiple runs.

    For each run, performs Groth16 setup using the specified circuit
    and measures its execution time.

    Args:
        zkp_setup_results_file: File path for saving ZKP setup benchmark results.
        runs: Number of benchmark runs to perform.

    Saves:
        The execution time of each ZKP setup run.
    """
    for run in range(1, runs + 1):
        result, elapsed = benchmark.benchmark_function(
            run_zkp_setup, config.CIRCUIT_NAME
        )

        benchmark.save_result(
            zkp_setup_results_file,
            experiment="ZKP_setup",
            run=run,
            parameters={},
            execution_time=elapsed
        )

        print(f"Setup: Run={run}, Time={elapsed:.6f}s")

def benchmark_kzg_setup(kzg_setup_results_file, runs, fast_mode = True):
    """
    Benchmarks KZG setup for different numbers of users and SRS sizes.

    For each N value, selects the corresponding D value, performs KZG
    setup multiple times, and measures its execution time.

    Args:
        kzg_setup_results_file: File path for saving KZG setup benchmark results.
        runs: Number of benchmark runs for each parameter combination.
        fast_mode: Whether to use fast mode for GF setup. Defaults to True.

    Saves:
        The execution time of each KZG setup run, together with the
        corresponding N and D parameter values.
    """
    N_values = [10, 100, 1000]
    for N in N_values:
        D = setup_kzg.get_D_value(N)
        for run in range(1, runs + 1):
            result, elapsed = benchmark.benchmark_function(
                run_kzg_setup, config.COMMS_DATA, N, D, fast_mode
            )

            benchmark.save_result(
                kzg_setup_results_file,
                experiment="KZG_setup",
                run=run,
                parameters={"N": N, "D": D},
                execution_time=elapsed
            )

            print(f"Setup: N={N}, D={D}, Run={run}, Time={elapsed:.6f}s")

def benchmark_zkp_proof(zkp_proof_results_file, runs):
    """
    Benchmarks Groth16 proof generation over multiple runs.

    For each run, generates the circuit input using a new
    user data record, then measures the execution time of proof generation.

    Args:
        zkp_proof_results_file: File path for saving proof generation
            benchmark results.
        runs: Number of benchmark runs to perform.

    Saves:
        The execution time of each proof generation run.
    """
    user_data = config.USER_DATA
    comms_data = config.COMMS_DATA
    col_names = ["email_address", "password", "first_name", "last_name", "age", "sex", "education", "marital_status"]
    indexes = [i for i in range(runs)]
    for index in indexes:
        create_input(col_names, user_data, index, comms_data)
        result, elapsed = benchmark.benchmark_function(
            run_zkp_proof, config.CIRCUIT_NAME
        )
        benchmark.save_result(
            zkp_proof_results_file,
            experiment="ZKP_proof",
            run=index + 1,
            parameters={},
            execution_time=elapsed
        )
        print(f"Setup: Run={index + 1}, Time={elapsed:.6f}s")

def benchmark_zkp_verification(zkp_verification_results_file, runs):
    """
    Benchmarks Groth16 verification over multiple runs.

    For each run, generates the circuit input using a new
    user data record, creates a new proof and then measures the execution 
    time of proof verification.

    Args:
        zkp_verification_results_file: File path for saving verification
            benchmark results.
        runs: Number of benchmark runs to perform.

    Saves:
        The execution time of each verification run.
    """
    user_data = config.USER_DATA
    comms_data = config.COMMS_DATA
    col_names = ["email_address", "password", "first_name", "last_name", "age", "sex", "education", "marital_status"]
    indexes = [i for i in range(runs)]
    for index in indexes:
            create_input(col_names, user_data, index, comms_data)
            run_zkp_proof(config.CIRCUIT_NAME)
            result, elapsed = benchmark.benchmark_function(
                run_zkp_verification
            )
            benchmark.save_result(
                zkp_verification_results_file,
                experiment="ZKP_verify",
                run=index + 1,
                parameters={},
                execution_time=elapsed
            )
            print(f"Setup: Run={index + 1}, Time={elapsed:.6f}s")

def benchmark_kzg_verification(kzg_verification_results_file, runs):
    """
    Benchmarks KZG membership verification for a given number of users.

    For each N value, performs KZG setup to generate the q polynomial,
    SRS, and membership polynomials w. It then measures the execution time
    of membership verification over multiple runs.

    Args:
        kzg_verification_results_file: File path for saving KZG
            verification benchmark results.
        runs: Number of verification benchmark runs.

    Saves:
        The execution time of each verification run, together with
        the corresponding N and D parameter values.
    """
    N_values = [10, 100, 1000]
    for N in N_values:
        D = setup_kzg.get_D_value(N)
        tau, q_tau_G1, w_tau_G2s, srs_kzg = run_kzg_setup(config.COMMS_DATA, N, D)
        for run in range(1, runs + 1):
            w_tau_G2 = w_tau_G2s[(run - 1) % N]
            result, elapsed = benchmark.benchmark_function(
                run_kzg_verification, q_tau_G1, srs_kzg, w_tau_G2
            )

            benchmark.save_result(
                kzg_verification_results_file,
                experiment="KZG_verify",
                run=run,
                parameters={"N": N, "D": D},
                execution_time=elapsed
            )

            print(f"Setup: N={N}, D={D}, Run={run}, Time={elapsed:.6f}s")

def benchmark_server_decision(server_decision_results_file, runs):
    """
    Benchmarks the server-side decision process over multiple runs.

    For each run, generates the input data, creates and executes a ZKP proof,
    extracts the public commitments (com_in and com_mem), and measures the
    execution time of the server-side decision function.

    The execution time for each run is saved to the specified results file.

    Args:
        server_decision_results_file: Path to the file for storing benchmark results.
        runs (int): Number of benchmark runs to perform.

    Saves:
        The execution time of each decision run
    """
    user_data = config.USER_DATA
    comms_data = config.COMMS_DATA
    col_names = ["email_address", "password", "first_name", "last_name", "age", "sex", "education", "marital_status"]
    indexes = [i for i in range(runs)]
   
    for run in range(1, runs + 1):
        row = create_input_and_return_vals(col_names, user_data, run-1, comms_data)
        run_zkp_proof(config.CIRCUIT_NAME)
        new_col_names = row.index.tolist()
        # Make sure the first index is com_in and the second is com_mem
        indexes = [0, 1]
        comms = data_extractor.extract_public_commitments(indexes, config.PUBLIC_JSON)
        com_in = comms[0]
        com_mem = comms[1]
        result, elapsed = benchmark.benchmark_function(
            sim_decision, row, new_col_names, com_in, com_mem
        )

        benchmark.save_result(
            server_decision_results_file,
            experiment="Server_decide",
            run=run,
            parameters={},
            execution_time=elapsed
        )

        print(f"Setup: Run={run}, Time={elapsed:.6f}s")

def benchmark_communication_overhead(runs):
    """
    Benchmarks the average communication size of the original input and
    the ZKP-based approach over multiple runs.

    For each run, measures the size of the original input record, generates
    a ZKP proof, and measures the serialized sizes of the proof and public
    inputs in JSON format.

    Args:
        runs (int): Number of benchmark runs to perform.

    Returns:
        tuple: A tuple containing:
            - average_original_input_size (float): Average original input
              size in bytes.
            - average_proof_json_size (float): Average proof.json size
              in bytes.
            - average_public_json_size (float): Average public.json size
              in bytes.
    """
    user_data = config.USER_DATA
    comms_data = config.COMMS_DATA
    col_names = ["email_address", "password", "first_name", "last_name", "age", "sex", "education", "marital_status"]
    data = data_extractor.get_rows(user_data, col_names, runs)
    
    input_sizes = [
        len(",".join(row.astype(str)).encode("utf-8"))
        for _, row in data.iterrows()
    ]

    average_original_input_size = sum(input_sizes) / len(input_sizes)

    proof_sizes = []
    public_sizes = []
    indexes = [i for i in range(runs)]
    for index in indexes:
        create_input(col_names, user_data, index, comms_data)
        run_zkp_proof(config.CIRCUIT_NAME)
        proof_sizes.append(os.path.getsize(config.PROOF_JSON))
        public_sizes.append(os.path.getsize(config.PUBLIC_JSON))

        print(f"Setup: Run={index + 1}")

    average_proof_json_size = sum(proof_sizes) / runs
    average_public_json_size = sum(public_sizes) / runs
    return average_original_input_size, average_proof_json_size, average_public_json_size

def benchmark_components(components, runs):
    """
    Runs selected ZKP and KZG benchmarks.

    Executes the benchmark functions corresponding to the components
    specified in the input list. Each selected benchmark is run a runs number 
    of times.

    Args:
        components: List of benchmark components to execute. 
        runs: Number of runs

    Saves:
        Benchmark results to separate CSV files in config.RESULTS_DIR
        for each selected component.
    """
    if "zkp_setup" in components:
        zkp_setup_results_file = os.path.join(config.RESULTS_DIR, "zkp_setup_results.csv")
        runs = 100
        benchmark_zkp_setup(zkp_setup_results_file, runs)
    if "kzg_setup" in components:
        kzg_setup_results_file = os.path.join(config.RESULTS_DIR, "kzg_setup_results.csv")
        runs = 100
        benchmark_kzg_setup(kzg_setup_results_file, runs)
    if "zkp_proof" in components:
        zkp_proof_results_file = os.path.join(config.RESULTS_DIR, "zkp_proof_results.csv")
        runs = 100
        benchmark_zkp_proof(zkp_proof_results_file, runs)
    if "zkp_verify" in components:
        zkp_verification_results_file = os.path.join(config.RESULTS_DIR, "zkp_verification_results.csv")
        runs = 100
        benchmark_zkp_verification(zkp_verification_results_file, runs)
    if "kzg_verify" in components:
        kzg_verification_results_file = os.path.join(config.RESULTS_DIR, "kzg_verification_results.csv")
        runs = 100
        benchmark_kzg_verification(kzg_verification_results_file, runs)
    if "server_decide" in components:
        server_decide_results_file = os.path.join(config.RESULTS_DIR, "server_decide_results.csv")
        runs = 100
        benchmark_server_decision(server_decide_results_file, runs)
    if "communication" in components:
        runs = 1000
        original_input_size, proof_json_size, public_json_size = benchmark_communication_overhead(runs)
        print(f"Average input size: {original_input_size:.2f} bytes")
        print(f"Average proof.json size: {proof_json_size:.2f} bytes")
        print(f"Average public.json size: {public_json_size:.2f} bytes")
        
if __name__ == "__main__":
    runs = 1000
    components = [
    #    "zkp_setup",
    #    "zkp_proof",
    #    "zkp_verify",
    #    "kzg_setup",
    #    "kzg_verify",
       "server_decide",
    #     "communication"
    ]
    benchmark_components(components, runs)
    

