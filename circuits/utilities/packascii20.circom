pragma circom 2.2.3;

template PackAscii20() {
    signal input ascii[20];
    signal output packed;

    var power = 1;
    var result = 0;

    for (var i = 0; i < 20; i++) {
        result += ascii[i] * power;
        power *= 128;
    }

    packed <== result;
}