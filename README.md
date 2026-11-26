# input-validation
Code for the Outsourced Client Input Validation Protocol for Web Services Using Zero-Knowledge Proofs

## Prerequisites and Installation

The following software and dependencies are required:

- Python 3
- Rust and Cargo
- Node.js and npm
- Circom
- snarkjs
- circomlib
- Python packages: `circomlibpy`, `pandas`, `py-ecc`, and `galois`

### 1. Rust and Cargo

Install Rust and Cargo using rustup:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Cargo is Rust's package manager and build tool.

### 2. Circom and snarkjs

Clone the [Circom repository](https://github.com/iden3/circom), then build and install Circom:

```bash
cargo build --release
cargo install --path circom
```

Install snarkjs and circomlib using npm:

```bash
npm install -g snarkjs
npm install circomlib
```

Circom is used to compile zero-knowledge circuits, while snarkjs supports Groth16 setup, proof generation, and verification.

The `circomlib` library provides the Circom circuit templates used in this project, including Poseidon hashing, bit decomposition, and comparison operations. These templates are installed in `node_modules/circomlib/circuits/`.

### 3. Python packages

Install the required packages:

```bash
python3 -m pip install circomlibpy pandas py-ecc galois
```

The packages provide the following functionality:

- `circomlibpy`: Python implementations of Circom-related cryptographic primitives.
- `pandas`: Dataset manipulation.
- `py-ecc`: Elliptic-curve and pairing operations.
- `galois`: Finite-field arithmetic.

### 4. Verify the installations

Run the following commands to verify that the required software is installed:

```bash
python3 --version
python3 -m pip --version
rustc --version
cargo --version
circom --version
node --version
npm --version
snarkjs --version
```
