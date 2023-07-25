import json
import yaml
import random
import string


def generate_random_string(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def safe_load_json_file(file_path: str):
    try:
        with open(file_path, "r") as file:
            parsed_json = json.load(file)
    except json.JSONDecodeError:
        parsed_json = []
    return parsed_json


def safe_load_yaml_file(file_path: str):
    try:
        with open(file_path, "r") as file:
            parsed_yaml = yaml.safe_load(file)
    except Exception:
        parsed_yaml = []
    return parsed_yaml


def safe_loads(json_string: str):
    try:
        parsed_json = json.loads(json_string)
    except json.JSONDecodeError:
        parsed_json = {}
    return parsed_json


def safe_json_dumps(content, file_path):
    with open(file_path, "w") as json_file:
        json.dump(content, json_file)


def safe_txt_dumps(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)
