pragma circom 2.2.3;

include "circomlib/circuits/comparators.circom";

template IsValidName() {
    // Hardcoded to max 20 characters
    signal input name[20];
    signal input length;

    // Non-empty
    // 2^4 < 20 < 2^5, so 5 bits are needed for the comparator
    component minLength = LessThan(5);
    minLength.in[0] <== 0;
    minLength.in[1] <== length;
    minLength.out === 1;

    // Also check if length is maximum 20
    component maxLength = LessEqThan(5);
    maxLength.in[0] <== length;
    maxLength.in[1] <== 20;
    maxLength.out === 1;

    // Each character must be ASCII (0–127)
    component asciiCheck[20];
    for (var i = 0; i < 20; i++) {
        asciiCheck[i] = LessThan(8);
        asciiCheck[i].in[0] <== name[i];
        asciiCheck[i].in[1] <== 128;
        asciiCheck[i].out === 1;
    }

    // Unused positions must be zero
    component isUnused[20];

    for (var i = 0; i < 20; i++) {
        isUnused[i] = LessThan(5);
        isUnused[i].in[0] <== length;
        isUnused[i].in[1] <== i + 1;

        isUnused[i].out * name[i] === 0;
    }
}