import bcrypt
from flask import request, jsonify
from main_app.models.user.user import User

def generate_encoded_string(data: dict, fields_to_encode: list) -> str:
    parts = []

    for field in fields_to_encode:
        value = data.get(field)

        if type(value) == str:
            parts.append("#$" + value)
        elif type(value) == list:
            for item in value:
                parts.append("#$" + str(item))
        elif type(value) == dict:
            for key in value:
                parts.append("#$" + str(key) + ":" + str(value[key]))
        elif value is not None:
            parts.append("#$" + str(value))

    final_string = " ".join(parts)

    hashed = bcrypt.hashpw(final_string.encode(), bcrypt.gensalt(rounds=12)).decode()
    reversed_hash = hashed[::-1]

    return reversed_hash

def decode():
    try:
        data = request.get_json()
        encoded = data.get('encoded_string')
        parts = int(data.get('parts'))

        if not encoded:
            return jsonify({"success": False, "error": "No 'encoded_string' provided"}), 400

        reversed_back = encoded[::-1]
        length = len(reversed_back)
        part_size = (length + 3) // 4

        # result = {
        #     "R1": reversed_back[0:part],
        #     "R2": reversed_back[part:part * 2],
        #     "R3": reversed_back[part * 2:part * 3],
        #     "R4": reversed_back[part * 3:]
        # }
        result = {}
        for i in range(parts):
            start = i * part_size
            end = start + part_size
            result[f"R{i + 1}"] = reversed_back[start:end]

        return jsonify({"success": True, "decoded_parts": result}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

