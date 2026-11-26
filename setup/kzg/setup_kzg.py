from circomlibpy.poseidon import PoseidonHash
from data import data_extractor
from inputs import generate_input
import pandas as pd
import config
import galois
from py_ecc.optimized_bn128 import curve_order, G1, G2, multiply
import secrets

D_MAX = 100 # Maximum size of SRS

def computeCommitment(inputs):
    """
    Compute a Poseidon commitment for the given list of inputs.

    Args:
        inputs: List of field elements.

    Returns:
        Poseidon hash of the input list.
    """
    poseidon = PoseidonHash()
    n = len(inputs)
    return poseidon.hash(n, inputs)

def storeCommitments(col_names, dataset, n_users, comms_data):
    """
    Generate and store Poseidon commitments for each user in a dataset.

    For each user, generates a random field element, prepares the user's
    data for Poseidon hashing, and computes a commitment. Stores the random
    field element and commitment alongside the original data in a CSV file.

    Args:
        col_names: List of names of the dataset columns to include.
        dataset: Input dataset as a dataframe
        n_users: Number of users to process.
        comms_data: Output CSV file path for storing the commitments.
    """
    rows = data_extractor.get_rows(dataset, col_names, n_users)
    df_mem = rows.copy(deep=True)
    df_mem["r_mem"] = None
    df_mem["com_mem"] = None
    for index, row in rows.iterrows():
        r_mem = generate_input.random_field_element()
        row_dict = data_extractor.circomify(row, col_names)
        row_dict["r_mem"] = r_mem
        _, pos_data = data_extractor.makePoseidonFriendly([row_dict])
        com_mem = computeCommitment(pos_data[0])
        df_mem.at[index, "r_mem"] = r_mem
        df_mem.at[index, "com_mem"] = com_mem    
    df_mem.to_csv(comms_data, index=False)
    print(f"Commitments saved to: {comms_data}")

def extract_comm_mem_from_dataset(indexes, comms_data):
    """
    Extracts commitment values from the 'com_mem' column of a CSV file
    at the specified row indexes.

    Args:
        comms_data (str): Path to the dataset containing commitments.
        indexes (list[int]): List of row indexes to extract.

    Returns:
        list[int]: Commitment values corresponding to the specified indexes.

    Raises:
        IndexError: If any index is out of range.
        KeyError: If the CSV does not contain a 'com_mem' column.
    """
    df = pd.read_csv(comms_data)

    if "com_mem" not in df.columns:
        raise KeyError("CSV does not contain a 'com_mem' column")

    if any(i < 0 or i >= len(df) for i in indexes):
        raise IndexError("One or more indexes are out of range")

    return [int(df.iloc[i]["com_mem"]) for i in indexes]

def evaluate_at_tau(q, ws, GF):
    """Sample a random tau in F_p and evaluate q and each w at it.

    Args:
        q (galois.Poly): Polynomial over GF to evaluate.
        ws (Sequence[galois.Poly]): Polynomials over GF to evaluate.
        GF (type): The galois field class (F_p) tau is sampled from.

    Returns:
        tuple: (tau, q_tau, w_taus), where
            tau (galois.FieldArray): Random scalar in F_p (0 is possible).
            q_tau (galois.FieldArray): q(tau).
            w_taus (list[galois.FieldArray]): w(tau) for each w in ws, in order.
    """
    tau = GF(secrets.randbelow(curve_order)) 
    q_tau = q(tau)
    w_taus = []
    for w in ws:
        w_taus.append(w(tau))
    return tau, q_tau, w_taus

def create_q_polynomial(comm_mems, GF):
    """Build the polynomial q(x) = prod_{c in comm_mems} (x - c) over GF.

    Args:
        comm_mems (Iterable[int]): Roots of q. Each value must be in [0, p-1],
            since GF(c) raises ValueError for out-of-range ints.
        GF (type): The galois field class (F_p) the polynomial is defined over.

    Returns:
        galois.Poly: Monic polynomial over GF of degree len(comm_mems) whose
            roots are exactly the elements of comm_mems. Returns the constant
            polynomial 1 if comm_mems is empty.
    """
    x = galois.Poly.Identity(GF)
    q = galois.Poly.One(GF)
    for c in comm_mems:
        q *= (x - GF(c))
    return q

def create_w_polynomial(q, comm_mem, GF):
    """Compute the quotient w(x) = q(x) / (x - c) over GF, requiring exact division.

    Args:
        q (galois.Poly): Polynomial over GF, expected to have c as a root.
        comm_mem (int): The value c. Must be in [0, p-1], since GF(c) raises
            ValueError for out-of-range ints.
        GF (type): The galois field class (F_p) the polynomials are defined over.

    Returns:
        galois.Poly: The quotient w(x) of degree deg(q) - 1, satisfying
            q(x) = (x - c) * w(x).

    Raises:
        ValueError: If (x - c) does not divide q, i.e. q(c) != 0.
    """
    x = galois.Poly.Identity(GF)
    x_minus_c = x - GF(comm_mem)   

    w, r = divmod(q, x_minus_c)
    if r != 0:
        raise ValueError(f"(x - c) does not divide q: q(c) = {int(q(GF(comm_mem)))} != 0")     
    return w

def create_w_polynomials(q, comm_mems, GF):
    """Compute w(x) = q(x) / (x - c) for each c in comm_mems.

    Args:
        q (galois.Poly): Polynomial over GF that has every c in comm_mems as a root.
        comm_mems (Iterable[int]): The values c. Each must be in [0, p-1],
            since GF(c) raises ValueError for out-of-range ints.
        GF (type): The galois field class (F_p) the polynomials are defined over.

    Returns:
        list[galois.Poly]: The quotients w_i(x), in the same order as comm_mems,
            each satisfying q(x) = (x - c_i) * w_i(x).

    Raises:
        ValueError: If (x - c) does not divide q for any c in comm_mems.
    """
    return [create_w_polynomial(q, comm_mem, GF) for comm_mem in comm_mems]

def get_curve_point_G1(poly_tau):
    """Map a scalar in F_p to the G1 point poly_tau * G1.

    Args:
        poly_tau (galois.FieldArray | int): Scalar to multiply the G1 generator
            by, typically a polynomial evaluated at tau, e.g. q(tau) or w(tau).
            It must live in the BN254 scalar field (p == curve_order).

    Returns:
        Point in G1 (py_ecc point): poly_tau * G1. If poly_tau is 0, this is the
            point at infinity: None with py_ecc.bn128, or a Z = 0 point (Z1)
            with py_ecc.optimized_bn128.
    """
    return multiply(G1, int(poly_tau))

def get_curve_point_G2(poly_tau):
    """Map a scalar in F_p to the G2 point poly_tau * G2.

    Args:
        poly_tau (galois.FieldArray | int): Scalar to multiply the G1 generator
            by, typically a polynomial evaluated at tau, e.g. q(tau) or w(tau).
            It must live in the BN254 scalar field (p == curve_order).

    Returns:
        Point in G1 (py_ecc point): poly_tau * G1. If poly_tau is 0, this is the
            point at infinity: None with py_ecc.bn128, or a Z = 0 point (Z1)
            with py_ecc.optimized_bn128.
    """
    return multiply(G2, int(poly_tau))


def generate_KZG_SRS(tau, D):
    """Compute the G1 powers-of-tau SRS [tau^0 * G1, tau^1 * G1, ..., tau^D * G1].

    Args:
        tau (galois.FieldArray | int): The secret evaluation point. Reduced
            mod curve_order before use, so it should live in the BN254 scalar
            field (p == curve_order).
        D (int): Maximum power of tau. The result has D + 1 entries.

    Returns:
        list: D + 1 G1 points (py_ecc points), where entry i is tau^i * G1.
            Entry 0 is the G1 generator and entry 1 is tau * G1.
    """
    t = int(tau) % curve_order
    srs_g1 = []
    t_i = 1
    for _ in range(D + 1):
        srs_g1.append(multiply(G1, t_i))
        t_i = (t_i * t) % curve_order
    return srs_g1

def initialize_GF(fast_mode = True):
    """
    Initialize and return a Galois field using the specified curve order.

    Args:
        fast_mode (bool): If True, use optimized field initialization settings
            to skip primality verification and primitive-element search.
            If False, use the default Galois group initialization.

    Returns:
        GF: The initialized Galois field.
    """
    if fast_mode:
        print("initialization GF ...")
        GF = galois.GF(
            curve_order,
            primitive_element=2,   # skip primitive-root search (any valid element; 2 is just a placeholder)
            verify=False,          # skip primality re-check (you just generated a prime)
            compile="python-calculate",
        )
        print("initialization complete!")
    else:
        print("initialization GF ...")
        GF = galois.GF(curve_order)
        print("initialization complete!")
    return GF

def get_D_value(N):
    """
    Returns the value of D, the number of user updates before system update.

    Args:
        N: Number of users
    Returns:
        D: According to the number of users
    """
    if N == 10:
        D = 5
    elif N == 100:
        D = 10
    else:
        D = 100
    return D

def run_setup(comms_data, N, D, fast_mode = True, return_q_tau=False):
    """
    Generate the KZG setup parameters for polynomial commitments
    associated with the dataset.

    Args:
        comms_data: Dataset containing the membership commitments.
        N (int): Number of commitments to include in the setup.
        D (int): Maximum polynomial degree for the KZG SRS.
        fast_mode (bool): If True, use optimized field initialization settings
            to skip primality verification and primitive-element search.
            If False, use the default Galois group initialization.
        return_q_tau (bool): If True, additionally return q(tau) as a field
            element, alongside its G1 curve point representation.

    Returns:
        tuple:
            tau: Random evaluation point used in the setup.
            q_tau_G1: Evaluation of the q polynomial at tau, represented
                as a G1 curve point.
            w_tau_G2s: Evaluations of the w polynomials at tau,
                represented as G2 curve points.
            srs_kzg: KZG structured reference string (SRS).
    """
    GF = initialize_GF(fast_mode)
    indexes = [i for i in range(N)]
    comm_mems = extract_comm_mem_from_dataset(indexes, comms_data)
    q = create_q_polynomial(comm_mems, GF)
    ws = []
    for i in range(N):
        w = create_w_polynomial(q, comm_mems[i], GF)
        ws.append(w)
    tau, q_tau, w_taus = evaluate_at_tau(q, ws, GF)
    q_tau_G1 = get_curve_point_G1(q_tau)
    w_tau_G2s = [get_curve_point_G2(w_tau) for w_tau in w_taus]
    D = get_D_value(N)
    srs_kzg = generate_KZG_SRS(tau, D)
    if return_q_tau:
        return tau, q_tau, q_tau_G1, w_tau_G2s, srs_kzg
    return tau, q_tau_G1, w_tau_G2s, srs_kzg

def add_new_users(comms_data, K, N, tau, q_tau):
    D = get_D_value(N)
    if K > D:
        raise ValueError(f"K must not exceed D = {D}")
    indexes = [i for i in range(N + K)]
    comm_mems = extract_comm_mem_from_dataset(indexes, comms_data)
    a_tau = tau
    b_tau = 1
    for i in range(K):
        factor = (tau - comm_mems[i])
        a_tau = a_tau * factor
        b_tau = b_tau * factor
        q_tau = q_tau * factor
    q_tau_G1 = get_curve_point_G1(q_tau)
    a_tau_G1 = get_curve_point_G1(a_tau)
    b_tau_G1 = get_curve_point_G1(b_tau)
    return q_tau_G1, a_tau_G1, b_tau_G1


if __name__ == "__main__":
    input = [12345, 67890]
    input = [41108464160547525560673372823582107946635530522687329, 0, 25, 2317298691419232147784653530, 13, 18383778615282859685558310136127089202738176375328218413374722091931525971968]
    input = [41108464160547525560673372823582107946635530522687329, 0, 25, 2317298691419232147784653530, 13, 3012344433838317940200172797240662421078851130811753072263076347494677899676]
    result = computeCommitment(input)
    print(f"The Poseidon hash commitment is {result}")
    comms_data = config.COMMS_DATA
    N = 2
    D = 10
    
    
   




    # print("tau:", tau)
    # print("q_tau:", q_tau)
    # print("w_tau:", w_taus)
    
    # srs_kzg = generate_KZG_SRS(tau, D)
    # print(srs_kzg)