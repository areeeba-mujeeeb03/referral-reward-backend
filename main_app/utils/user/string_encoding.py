from typing import final

import bcrypt

def encode_str(str):
    if not isinstance(str):
        raise TypeError("Input must be a string.")

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)

    number = 2
    encoded_string = ""
    while number > 0:
        remainder = number % base
        encoded_string = alphabet[remainder] + encoded_string
        number //= base
    return encoded_string

def generate_encoded_string(info: dict, fields_to_encode: list):
    # Step 1: Extract values
    values = [str(info.get(field, "")) for field in fields_to_encode]

    # Step 2: Add special characters before each value
    original_string = "".join([f"#$" + val for val in values])

    # Step 3: Reverse the string
    reversed_string = original_string[::-1]

    # Step 4: Hash with bcrypt
    encrypted_string = bcrypt.hashpw(reversed_string.encode(), bcrypt.gensalt()).decode()

    # Step 5: Reverse the encrypted string again
    final_string = encrypted_string[::-1]

    # Step 6: Map each encoded field to R1, R2
    length = len(final_string)
    part_size = (length) // 4

    result = {
        "date": final_string[0:part_size],
        "age": final_string[part_size:part_size * 2],
        "gender": final_string[part_size * 2:part_size * 3],
        "arn_id": final_string[part_size * 3:]
    }
    print(encrypted_string)
    return result