import subprocess

def verify_proof():
    subprocess.run(
        [
            "npx", "snarkjs", "groth16", "verify",
            "outputs/verification_key.json",
            "outputs/public.json",
            "outputs/proof.json",
        ],
        check=True,
    )
    print("Proof verification successful!")

if __name__ == "__main__":
    verify_proof()