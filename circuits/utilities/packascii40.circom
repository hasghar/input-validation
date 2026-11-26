pragma circom 2.2.3;

template PackAscii40() {
    signal input ascii[40];
    signal output packed1;
    signal output packed2;

    var p1 = 0;
    var p2 = 0;
    var power = 1;

    // Maximum 36 ASCII characters (7-bits each) fit in one BN128 field element
    // Dividing into two values 
    for (var i = 0; i < 36; i++) {
        p1 += ascii[i] * power;
        power *= 128;
    }

    power = 1;

    for (var i = 36; i < 40; i++) {
        p2 += ascii[i] * power;
        power *= 128;
    }

    packed1 <== p1;
    packed2 <== p2;
}