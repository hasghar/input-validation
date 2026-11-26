pragma circom 2.2.3;
include "fields/isvalidname.circom";
include "fields/isvalidage.circom";
include "fields/isvalidsex.circom";
include "fields/isvalideducation.circom";
include "fields/isvalidmaritalstatus.circom";
include "fields/isvalidemailaddress.circom";
include "fields/isvalidpassword.circom";
include "utilities/packascii20.circom";
include "utilities/packascii40.circom";
include "circomlib/circuits/poseidon.circom";

template ValidateFields() {
    signal input email_address[40];
    signal input email_address_length;

    signal input password[20];
    signal input password_length;

    signal input first_name[20];
    signal input first_name_length;

    signal input last_name[20];
    signal input last_name_length;

    signal input age;
    signal input sex;
    signal input education;
    signal input marital_status;
    signal input r_in;
    signal input r_mem;

    component email_address_check = IsValidEmailAddress();

    for (var i = 0; i < 40; i++) {
        email_address_check.email_address[i] <== email_address[i];
    }

    email_address_check.email_address_length <== email_address_length;

    component password_check = IsValidPassword();

    for (var i = 0; i < 20; i++) {
        password_check.password[i] <== password[i];
    }

    password_check.password_length <== password_length;

    component firstName = IsValidName();
    component lastName = IsValidName();

    for (var i = 0; i < 20; i++) {
        firstName.name[i] <== first_name[i];
        lastName.name[i] <== last_name[i];
    }

    firstName.length <== first_name_length;
    lastName.length <== last_name_length;

    component age_check = IsValidAge();
    age_check.age <== age;

    component sex_check = IsValidSex();
    sex_check.sex <== sex;

    component education_check = IsValidEducation();
    education_check.education <== education;

    component marital_check = IsValidMaritalStatus();
    marital_check.marital_status <== marital_status;

    // Poseidon commitment to input signals
    signal output com_in;

    // Poseidon commitment to membership signals
    signal output com_mem;

    component pack_email_address = PackAscii40();
    component pack_password = PackAscii20();
    component pack_first_name = PackAscii20();
    component pack_last_name = PackAscii20();
    
    for (var i = 0; i < 20; i++) {
        pack_first_name.ascii[i] <== first_name[i];
        pack_last_name.ascii[i] <== last_name[i];
        pack_password.ascii[i] <== password[i];
    }

    for (var i = 0; i < 40; i++) {
        pack_email_address.ascii[i] <== email_address[i];
    }
    
    component poseidon1 = Poseidon(14);

    poseidon1.inputs[0] <== pack_email_address.packed1;
    poseidon1.inputs[1] <== pack_email_address.packed2;
    poseidon1.inputs[2] <== email_address_length;

    poseidon1.inputs[3] <== pack_password.packed;
    poseidon1.inputs[4] <== password_length;

    poseidon1.inputs[5] <== pack_first_name.packed;
    poseidon1.inputs[6] <== first_name_length;
    poseidon1.inputs[7] <== pack_last_name.packed;
    poseidon1.inputs[8] <== last_name_length;

    poseidon1.inputs[9] <== age;
    poseidon1.inputs[10] <== sex;
    poseidon1.inputs[11] <== education;
    poseidon1.inputs[12] <== marital_status;
  
    poseidon1.inputs[13] <== r_in;

    com_in <== poseidon1.out;

    component poseidon2 = Poseidon(6);

    poseidon2.inputs[0] <== pack_email_address.packed1;
    poseidon2.inputs[1] <== pack_email_address.packed2;
    poseidon2.inputs[2] <== email_address_length;

    poseidon2.inputs[3] <== pack_password.packed;
    poseidon2.inputs[4] <== password_length;

    poseidon2.inputs[5] <== r_mem;

    com_mem <== poseidon2.out;

    // Remove following public outputs. They are there for sanity check
    //signal output public_inputs[15];

    //public_inputs[0] <== pack_email_address.packed1;
    //public_inputs[1] <== pack_email_address.packed2;
    //public_inputs[2] <== email_address_length;
    //public_inputs[3] <== pack_password.packed;
    //public_inputs[4] <== password_length;

    //public_inputs[5] <== pack_first_name.packed;
    //public_inputs[6] <== first_name_length;
    //public_inputs[7] <== pack_last_name.packed;
    //public_inputs[8] <== last_name_length;
    //public_inputs[9] <== age;
    //public_inputs[10] <== sex;
    //public_inputs[11] <== education;
    //public_inputs[12] <== marital_status;

    //public_inputs[13] <== r_in;
    //public_inputs[14] <== r_mem;
}

component main = ValidateFields();