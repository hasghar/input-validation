pragma circom 2.2.3;

include "circomlib/circuits/bitify.circom";
include "circomlib/circuits/comparators.circom";

template IsValidAge() {
    signal input age;

    // age can be represented as a 7 bit integer (0 to 127)
    component bits = Num2Bits(7);
    bits.in <== age;

    // max age is 120
    component range = LessThan(7);
    range.in[0] <== age;
    range.in[1] <== 121;

    range.out === 1;
}