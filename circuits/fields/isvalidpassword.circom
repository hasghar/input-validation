pragma circom 2.2.3;

include "circomlib/circuits/comparators.circom";

template IsValidPassword() {
    signal input password[20];
    signal input password_length;

    // Length between 8 and 20.
    // 2^4 < 20 < 2^5. 
    // Comparison is between two arrays of length 5 bits
    component minLength = GreaterEqThan(5);
    minLength.in[0] <== password_length;
    minLength.in[1] <== 8;
    minLength.out === 1;

    // Again comparison is between two arrays of length 5 bits
    component maxLength = LessEqThan(5);
    maxLength.in[0] <== password_length;
    maxLength.in[1] <== 20;
    maxLength.out === 1;

    // Checks only active characters
    component active[20];

    // Character category indicators.
    signal isUpper[20];
    signal isLower[20];
    signal isDigit[20];
    signal isSpecial[20];

    // Running counters
    signal upperCount[21];
    signal lowerCount[21];
    signal digitCount[21];
    signal specialCount[21];

    // ASCII ranges for the different characters
    component upperMin[20];
    component upperMax[20];
    component lowerMin[20];
    component lowerMax[20];
    component digitMin[20];
    component digitMax[20];

    // Special characters: !@#$%^&*()-_=+
    var specialChars[14] = [
        33, 64, 35, 36, 37, 94, 38,
        42, 40, 41, 45, 95, 61, 43
    ];

    component specialCheck[20][14];
    signal specialSum[20][15];

    // Initialise counters to check if characters are there
    upperCount[0] <== 0;
    lowerCount[0] <== 0;
    digitCount[0] <== 0;
    specialCount[0] <== 0;

    for (var i = 0; i < 20; i++) {

        // Check whether position is active.
        active[i] = LessThan(5);
        active[i].in[0] <== i;
        active[i].in[1] <== password_length;

        // Inactive positions must be zero.
        (1 - active[i].out) * password[i] === 0;

        // Uppercase: A-Z (65-90).
        upperMin[i] = GreaterEqThan(8);
        upperMin[i].in[0] <== password[i];
        upperMin[i].in[1] <== 65;

        upperMax[i] = LessThan(8);
        upperMax[i].in[0] <== password[i];
        upperMax[i].in[1] <== 91;

        // This is 1 only if the character is within lower and upper limit of category
        isUpper[i] <== upperMin[i].out * upperMax[i].out;

        // Lowercase: a-z (97-122).
        lowerMin[i] = GreaterEqThan(8);
        lowerMin[i].in[0] <== password[i];
        lowerMin[i].in[1] <== 97;

        lowerMax[i] = LessThan(8);
        lowerMax[i].in[0] <== password[i];
        lowerMax[i].in[1] <== 123;

        isLower[i] <== lowerMin[i].out * lowerMax[i].out;

        // Digits: 0-9 (48-57).
        digitMin[i] = GreaterEqThan(8);
        digitMin[i].in[0] <== password[i];
        digitMin[i].in[1] <== 48;

        digitMax[i] = LessThan(8);
        digitMax[i].in[0] <== password[i];
        digitMax[i].in[1] <== 58;

        isDigit[i] <== digitMin[i].out * digitMax[i].out;

        // Special characters.
        specialSum[i][0] <== 0;

        for (var j = 0; j < 14; j++) {
            specialCheck[i][j] = IsEqual();
            specialCheck[i][j].in[0] <== password[i];
            specialCheck[i][j].in[1] <== specialChars[j];

            specialSum[i][j + 1] <== specialSum[i][j]
                + specialCheck[i][j].out;
        }

        isSpecial[i] <== specialSum[i][14];

        // Every active character must be in the allowed alphabet.
        active[i].out * (
            1 - isUpper[i] - isLower[i] - isDigit[i] - isSpecial[i]
        ) === 0;

        // Count character categories.
        upperCount[i + 1] <== upperCount[i]
            + active[i].out * isUpper[i];

        lowerCount[i + 1] <== lowerCount[i]
            + active[i].out * isLower[i];

        digitCount[i + 1] <== digitCount[i]
            + active[i].out * isDigit[i];

        specialCount[i + 1] <== specialCount[i]
            + active[i].out * isSpecial[i];
    }

    // Require at least one character from each category.
    component hasUpper = GreaterThan(5);
    hasUpper.in[0] <== upperCount[20];
    hasUpper.in[1] <== 0;
    hasUpper.out === 1;

    component hasLower = GreaterThan(5);
    hasLower.in[0] <== lowerCount[20];
    hasLower.in[1] <== 0;
    hasLower.out === 1;

    component hasDigit = GreaterThan(5);
    hasDigit.in[0] <== digitCount[20];
    hasDigit.in[1] <== 0;
    hasDigit.out === 1;

    component hasSpecial = GreaterThan(5);
    hasSpecial.in[0] <== specialCount[20];
    hasSpecial.in[1] <== 0;
    hasSpecial.out === 1;
}