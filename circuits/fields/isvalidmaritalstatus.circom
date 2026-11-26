pragma circom 2.2.3;

include "circomlib/circuits/bitify.circom";

template IsValidMaritalStatus() {
    signal input marital_status;
    signal intermediate;

    // This has 7 values: 0-6
    component bits = Num2Bits(3);
    bits.in <== marital_status;

    // Exclude unused value 7
    intermediate <== bits.out[0] * bits.out[1];
    intermediate * bits.out[2] === 0;
}