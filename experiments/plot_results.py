import json
import pandas as pd
import matplotlib.pyplot as plt
import config
import os

BLUE = "#3b6fb6"

def plot_kzg_setup(kzg_setup_results_file):
    """
    Plots KZG setup execution times against the number of users.

    Reads the benchmark results from a CSV file, calculates the mean and
    standard deviation for each (N, D) configuration, and plots the mean
    execution time with a shaded region representing ±2 standard deviations.

    Args:
        kzg_setup_results_file: File path containing KZG setup benchmark results.

    Saves:
        KZG setup plots in PNG and PDF formats in config.PLOTS_DIR.
    """

    plt.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    })
    
    df = pd.read_csv(kzg_setup_results_file)
    params = df["parameters"].apply(json.loads)
    df["N"] = params.apply(lambda p: p["N"])
    df["D"] = params.apply(lambda p: p["D"])

    g = df.groupby(["N", "D"])["execution_time"].agg(["mean", "std"]).reset_index()
    x, m, s = g["N"], g["mean"], g["std"]

    plt.rcParams["pdf.fonttype"] = 42
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(x, m - 2 * s, m + 2 * s, color=BLUE, alpha=0.2, label="mean ± 2 SD")
    ax.plot(x, m, "o-", color=BLUE, lw=2, ms=7, label="mean")

    for xi, mi in zip(x, m):
        ax.annotate(f"{mi:.2f}s", (xi, mi), textcoords="offset points",
                    xytext=(10, 10), ha="right")

    ax.set_xscale("log")
    #ax.set_yscale("log")
    ax.set_xticks(x)
    #ax.set_xticklabels([f"N={n}\nD={d}" for n, d in zip(g["N"], g["D"])])
    ax.set_xticklabels([f"$N={n}$" for n in g["N"]])
    ax.set_ylabel("Execution time (s)")
    #ax.set_title("KZG Setup: Execution Time vs Number of Users $N$")
    ax.grid(True, which="major", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(os.path.join(config.PLOTS_DIR, "kzg_setup.png"), dpi=200)
    fig.savefig(os.path.join(config.PLOTS_DIR, "kzg_setup.pdf"))
    print(f"Done! check {config.PLOTS_DIR} for plots")

def plot_kzg_verification(kzg_verification_results_file):
    """
    Plots KZG verification times against the number of users.

    Reads the benchmark results from a CSV file, calculates the mean and
    standard deviation for each (N, D) configuration, and plots the mean
    execution time with a shaded region representing ±2 standard deviations.

    Args:
        kzg_verificatin_results_file: File path containing KZG verification benchmark results.

    Saves:
        KZG verification plots in PNG and PDF formats in config.PLOTS_DIR.
    """
    plt.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    })

    df = pd.read_csv(kzg_verification_results_file)
    params = df["parameters"].apply(json.loads)
    df["N"] = params.apply(lambda p: p["N"])
    df["D"] = params.apply(lambda p: p["D"])

    g = df.groupby(["N", "D"])["execution_time"].agg(["mean", "std"]).reset_index()
    x, m, s = g["N"], g["mean"], g["std"]

    plt.rcParams["pdf.fonttype"] = 42
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(x, m - 2 * s, m + 2 * s, color=BLUE, alpha=0.2, label="mean ± 2 SD")
    ax.plot(x, m, "o-", color=BLUE, lw=2, ms=7, label="mean")

    for xi, mi in zip(x, m):
        ax.annotate(f"{mi:.2f}s", (xi, mi), textcoords="offset points",
                    xytext=(10, 10), ha="right")

    ax.set_xscale("log")
    ax.set_ylim(0, 1.5)  
    #ax.set_yscale("log")
    ax.set_xticks(x)
    #ax.set_xticklabels([f"$N={n}$\n$D={d}$" for n, d in zip(g["N"], g["D"])])
    ax.set_xticklabels([f"$N={n}$" for n in g["N"]])
    #ax.set_xticklabels([f"$N={n}$" for n in g["N"]])
    ax.set_ylabel("Execution time (s)")
    #ax.set_title("KZG Verification: Execution Time vs Number of Users $N$")
    ax.grid(True, which="major", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(os.path.join(config.PLOTS_DIR, "kzg_verify.png"), dpi=200)
    fig.savefig(os.path.join(config.PLOTS_DIR, "kzg_verify.pdf"))
    print(f"Done! check {config.PLOTS_DIR} for plots")

def plot_zkp_component(component, zkp_results_file):
    """
    Plots the distribution of execution times for a ZKP component.

    Reads benchmark results from a CSV file and generates a box plot
    showing the spread of execution times, including the median, minimum,
    maximum, and mean.

    Args:
        component: ZKP component to plot ("zkp_proof", "zkp_verify",
            or "zkp_setup").
        zkp_results_file: File path containing ZKP benchmark results.

    Saves:
        The component's execution time plots in PNG and PDF formats
        in config.PLOTS_DIR.
    """
    df = pd.read_csv(zkp_results_file)
    if component == "zkp_proof":
        name = "ZKP Proof Generation Time"
    elif component == "zkp_verify":
        name = "ZKP Verification Time"
    elif component == "zkp_setup":
        name = "ZKP Setup Time"
    elif component == "server_decide":
        name = "Server Decision"
    else:
        raise ValueError(f"Unknown component: {component!r}")

    v = df["execution_time"].to_numpy()

    plt.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    })

    fig, ax = plt.subplots(figsize=(4.5, 5))
    ax.boxplot(v, positions=[0], widths=0.5, patch_artist=True,
               whis=(0, 100), showfliers=False,           # whiskers = min to max, no dots
               medianprops=dict(color="k"),
               boxprops=dict(facecolor=BLUE, alpha=0.25, edgecolor=BLUE),
               whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE))
    ax.annotate(f"Mean = {v.mean():.3g} s", (0, v.max()),
                textcoords="offset points", xytext=(0, 10), ha="center", fontsize=16)

    ax.set_xticks([])
    #; ax.set_xticklabels([name])
    ax.set_ylabel("Execution time (s)")
    #ax.set_title(f"{name}", fontsize=10)
    ax.margins(y=0.2)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    fig.tight_layout()
    fig.savefig(os.path.join(config.PLOTS_DIR, "zkp_" + component + ".png"), dpi=200)
    fig.savefig(os.path.join(config.PLOTS_DIR, "zkp_" + component + ".pdf"))
    print(f"Done! check {config.PLOTS_DIR} for plots")

def plot_component(components):
    """
    Plots the results for the selected KZG and ZKP components.

    Calls the corresponding plotting functions for each component
    specified in the input list.

    Args:
        components: List of components to plot. Supported options are
            "kzg_setup", "kzg_verify", "zkp_setup", "zkp_verify",
            "zkp_proof", and "server_decide"

    Saves:
        Component plots in PNG and PDF formats in config.PLOTS_DIR.
    """
    if "kzg_setup" in components:
        kzg_setup_results_file = os.path.join(config.RESULTS_DIR, "kzg_setup_results.csv")
        plot_kzg_setup(kzg_setup_results_file)
    if "kzg_verify" in components:
        kzg_verification_results_file = os.path.join(config.RESULTS_DIR, "kzg_verification_results.csv")
        plot_kzg_verification(kzg_verification_results_file)
    if "zkp_setup" in components:
        zkp_results_file = os.path.join(config.RESULTS_DIR, "zkp_setup_results.csv")
        plot_zkp_component("zkp_setup", zkp_results_file)
    if "zkp_verify" in components:
        zkp_results_file = os.path.join(config.RESULTS_DIR, "zkp_verification_results.csv")
        plot_zkp_component("zkp_verify", zkp_results_file)
    if "zkp_proof" in components:
        zkp_results_file = os.path.join(config.RESULTS_DIR, "zkp_proof_results.csv")
        plot_zkp_component("zkp_proof", zkp_results_file)
    if "server_decide" in components:
        server_results_file = os.path.join(config.RESULTS_DIR, "server_decide_results.csv")
        plot_zkp_component("server_decide", server_results_file)

if __name__ == "__main__":
    components = [
        "zkp_setup",
        "kzg_setup",
        "zkp_proof",
        "zkp_verify",
        "kzg_verify",
        "server_decide"
    ]
    plot_component(components)

