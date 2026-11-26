pragma circom 2.2.3;

include "circomlib/circuits/bitify.circom";

template IsValidEducation() {
    signal input education;

    // This has 16 categories: 0-15
    component bits = Num2Bits(4);
    bits.in <== education;
}