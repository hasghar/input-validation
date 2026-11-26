pragma circom 2.2.3;

include "circomlib/circuits/comparators.circom";

template IsValidEmailAddress() {
    signal input email_address[40];
    signal input email_address_length;

    // At least one character before and after @ 
    component minLength = GreaterEqThan(6);
    minLength.in[0] <== email_address_length;
    minLength.in[1] <== 3;
    minLength.out === 1;

    // Check if the email_address_length is indeed within 40
    component maxLength = LessEqThan(6);
    maxLength.in[0] <== email_address_length;
    maxLength.in[1] <== 40;
    maxLength.out === 1;

    // Each character must be ASCII (0–127)
    component asciiCheck[40];
    for (var i = 0; i < 40; i++) {
        asciiCheck[i] = LessThan(8);
        asciiCheck[i].in[0] <== email_address[i];
        asciiCheck[i].in[1] <== 128;
        asciiCheck[i].out === 1;
    }

    signal isAt[40];
    component atCheck[40];

    var atCount = 0;

    for (var i = 0; i < 40; i++) {
        // Check whether character is '@' (ASCII 64).
        atCheck[i] = IsEqual();
        atCheck[i].in[0] <== email_address[i];
        atCheck[i].in[1] <== 64;

        isAt[i] <== atCheck[i].out;

        // Positions beyond length must be zero.
        // Implemented below using a position selector.
        atCount += isAt[i];
    }

    signal activeAtCount[41];
    component positionActive[40];

    activeAtCount[0] <== 0;

    // Exactly one '@' among the active characters.
    for (var i = 0; i < 40; i++) {
        // Compare two six bit values and check if i < email_address_length
        positionActive[i] = LessThan(6);
        positionActive[i].in[0] <== i;
        positionActive[i].in[1] <== email_address_length;

        // Count @ only in active positions.
        activeAtCount[i + 1] <== activeAtCount[i] +
            positionActive[i].out * isAt[i];

        // Inactive positions must be zero.
        // If active it equals email_address[i], else it equals 0
        (1 - positionActive[i].out) * email_address[i] === 0;
    }

    activeAtCount[40] === 1;

    // At least one character before '@'.
    isAt[0] === 0;

    // At least one character after '@'.
    signal lastChar[41];
    component lastCheck[40];

    lastChar[0] <== 0;

    for (var i = 0; i < 40; i++) {
        // Check if position i is the last character according to email_address_length
        lastCheck[i] = IsEqual();
        lastCheck[i].in[0] <== email_address_length;
        lastCheck[i].in[1] <== i + 1;

        // The following is 1 only if last character is '@'
        lastChar[i + 1] <== lastChar[i] +
            lastCheck[i].out * isAt[i];
    }

    // The last character cannot be '@'.
    lastChar[40] === 0;
}