import json

DEFAULT_FILE = "todo.json"


def load_todos(filename=DEFAULT_FILE) -> dict:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_todos(data: dict, filename=DEFAULT_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def clear_file(filename=DEFAULT_FILE):
    save_todos({}, filename)
