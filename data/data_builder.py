import pandas as pd
import os
import random
import secrets
import string

column_names = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education_num",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
    "native_country",
    "income",
]

# Add first name, last name, email address and password columns
def augment_dataset(dataset):
    df = pd.read_csv(
        dataset,
        header=None,
        names=column_names,
        skipinitialspace=True,
        na_values= "?",
    )
    
    df.insert(0, "password", "")
    df.insert(0, "email_address", "")
    df.insert(0, "last_name", "")
    df.insert(0, "first_name", "")
    df.to_csv(augmented_dataset, index=False)
    print(f"Saved {len(df)} records to {augmented_dataset}")

# See how dataset looks like
def read_dataset(dataset):
    df = pd.read_csv(dataset)
    print("Dataset shape:", df.shape)
    print(df.head())

# Extract first names by gender from the US Census 2020 data
def extract_first_names(dataset):
    male_names = []
    female_names = []       
    df = pd.read_excel(dataset)
    # clean up so first row is column headers
    df = df.iloc[1:]
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)

    for index, row in df.iterrows():
        first_name = row["FIRST NAME"]
        if row["MALE"] > row["FEMALE"]:
            male_names.append(first_name.capitalize())
        else:
            female_names.append(first_name.capitalize())             

    return male_names, female_names
  
# Extract last names from the US Census 2020 data
def extract_last_names(dataset):
    last_names = []
    df = pd.read_excel(dataset)
    # clean up so first row is column headers
    print(df.head())
    df = df.iloc[1:]
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)

    last_names = df["LAST NAME"].str.capitalize().tolist()
    return last_names

# Insert unique first name-last name pairs in main dataset
def insert_names(dataset, male_names, female_names, last_names):
    used_pairs = set()
    first_names = []
    assigned_last_names = []
    df = pd.read_csv(dataset)
    for gender in df["sex"]:
        names = female_names if gender == "Female" else male_names

        while True:
            first = random.choice(names)
            last = random.choice(last_names)

            if (first, last) not in used_pairs:
                used_pairs.add((first, last))
                first_names.append(first)
                assigned_last_names.append(last)
                break

    df["first_name"] = first_names
    df["last_name"] = assigned_last_names
    df.to_csv(dataset, index=False)
    print("names added")

# Insert email addresses from first name-last name with random domain
def insert_emails(dataset, domains):
    df = pd.read_csv(dataset)
    df["email_address"] = (
        df["first_name"].str.lower() + "." +
        df["last_name"].str.lower() + "@" +
        pd.Series(
            [random.choice(domains) for _ in range(len(df))],
            index=df.index
        )
    )
    df.to_csv(dataset, index=False)
    print("emails added")

# Generate strong password
def generate_password(length = 8, low_limit = 8, up_limit = 16):
    if length < low_limit or length > up_limit:
        raise ValueError(f"Password length must be between {low_limit} and {up_limit}.")

    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()-_=+"

    # Guarantee at least one character from each category
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Fill the remaining positions
    alphabet = uppercase + lowercase + digits + special
    password.extend(
        secrets.choice(alphabet) for _ in range(length - 4)
    )

    # Randomise character positions
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)

# Insert password in main dataset
def insert_passwords(dataset, low_limit, up_limit):
    df = pd.read_csv(dataset)
    df["password"] = [
        generate_password(random.randint(low_limit, up_limit), low_limit, up_limit)
        for _ in range(len(df))
    ]
    df.to_csv(dataset, index=False)
    print("passwords added")


if __name__ == "__main__":
    data_dir = ""
    dataset = os.path.join(data_dir, "adult", "adult.data")
    first_names_dataset = os.path.join(data_dir, "Names2020_FirstNames_Sex.xlsx")
    last_names_dataset = os.path.join(data_dir, "Names2020_LastNames_RaceHispanic.xlsx")
    augmented_dataset = os.path.join(data_dir, "augmented_adult.csv")
    # For length of passwords
    low_limit = 8
    up_limit = 16
    # augment_dataset(dataset)
    # male_names, female_names = extract_first_names(first_names_dataset)
    # print(len(male_names))
    # print(len(female_names))
    # last_names = extract_last_names(last_names_dataset)
    # print(last_names[:3])
    # print(len(last_names))
    # insert_names(augmented_dataset, male_names, female_names, last_names)
    # domains = ["example.com"]
    # insert_emails(augmented_dataset, domains)
    #read_dataset(augmented_dataset)
    #insert_passwords(augmented_dataset, low_limit, up_limit)
    read_dataset(augmented_dataset)
    