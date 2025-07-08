from typing import final
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher_suite = Fernet(key)


def custom_decode(encoded_string):
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#*%!$"
    shift = 5
    decoded = ""

    for ch in encoded_string:
        if ch in charset:
            idx = 0
            for i in range(len(charset)):
                if charset[i] == ch:
                    idx = i
                    break
            new_index = (idx - shift + len(charset)) % len(charset)
            decoded += charset[new_index]
        else:
            decoded += ch  # keep unknown characters as-is

    return decoded
def generate_encoded_string(info: dict, fields_to_encode: list):
    # Step 1: Extract values
    values = [str(info.get(field, "")) for field in fields_to_encode]

    # Step 2: Add special characters before each value
    original_string = "".join([f"#$" + val for val in values])

    # Step 3: Reverse the string
    reversed_string = original_string[::-1]

    # Step 4: Hash with bcrypt
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#*%!$"
    shift = 5
    encoded = ""

    for ch in reversed_string:
        if ch in charset:
            idx = 0
            for i in range(len(charset)):
                if charset[i] == ch:
                    idx = i
                    break
            new_index = (idx + shift) % len(charset)
            encoded += charset[new_index]
        else:
            encoded += ch
    encrypted_string = encoded

    # Step 5: Reverse the encrypted string again
    final_string = encrypted_string[::-1]

    # Step 6: Map each encoded field to R1, R2
    length = len(final_string)
    part_size = length // 4
    result = {
        "date": final_string[0:part_size],
        "age": final_string[part_size:part_size * 2],
        "gender": final_string[part_size * 2:part_size * 3],
        "arn_id": final_string[part_size * 3:]
    }
    print(custom_decode(final_string))
    return result
