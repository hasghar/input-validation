import json
import config
from py_ecc.optimized_bn128 import G1, G2, multiply, add, neg, pairing, final_exponentiate, FQ12

def extract_com_mem_from_json(json_file):
    """
    Extracts the commitment value from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing the commitment
            value at index 1.

    Returns:
        int: Commitment value converted to an integer.
    """
    with open(json_file, "r") as f:
        data = json.load(f)
    
    com_mem = int(data[1])
    return com_mem

def verify_membership(q_tau_G1, srs_kzg, w_tau_G2, c):
    """
    Verify membership using a KZG polynomial commitment pairing equation.

    Checks whether the supplied commitment value c satisfies the
    membership verification equation:

        e(q(t)G1, G2) = e(tG1 - cG1, w(t)G2)
        => e(q(t)G1, G2) * e(-(tG1 - cG1), w(t)G2) = 1
        => e(q(t)G1, G2) * e(-(SRS[1] - cG1), w(t)G2) = 1

    Args:
        q_tau_G1: Evaluation of the q polynomial at tau, represented
            as a G1 curve point.
        srs_kzg: KZG structured reference string containing the
            powers of tau in G1.
        w_tau_G2: Evaluation of the corresponding w polynomial at tau,
            represented as a G2 curve point.
        c: Commitment value whose membership is being verified.

    Returns:
        bool: True if the pairing equation holds (membership verified),
            False otherwise.
    """
    R = add(srs_kzg[1], neg(multiply(G1, c)))
    result = pairing(G2, q_tau_G1) * pairing(w_tau_G2, neg(R))
    return final_exponentiate(result) == FQ12.one()

if __name__ == "__main__":
    json_file = config.PUBLIC_JSON
    com_mem = extract_com_mem_from_json(json_file)
    print("Membership commitment is:", com_mem)

