import bcrypt

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
    result_parts = {}
    for i, field in enumerate(fields_to_encode):
        result_parts[f"R{i + 1}"] = info.get(field, "")

    return {
        "original_string": original_string,
        "final_string": final_string,
        "parts": result_parts
    }