import time
import csv
import os
import json

def benchmark_function(func, *args, **kwargs):
    """
    Execute a function and measure its execution time.

    Args:
        func (callable): Function to benchmark.
        *args: Positional arguments passed to the function.
        **kwargs: Keyword arguments passed to the function.

    Returns:
        tuple:
            result: Return value of the executed function.
            elapsed (float): Execution time in seconds.
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start

    return result, elapsed


def save_result(filename, experiment, run, parameters, execution_time):
    """
    Append an individual benchmark result to a CSV file.

    Args:
        filename (str): CSV output filename.
        experiment (str): Name of the experiment.
        run (int): Experiment run number.
        parameters (dict): Experiment-specific parameters.
        execution_time (float): Execution time in seconds.
    """
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "experiment",
                "run",
                "parameters",
                "execution_time"
            ]
        )

        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow({
            "experiment": experiment,
            "run": run,
            "parameters": json.dumps(parameters),
            "execution_time": execution_time
        })

