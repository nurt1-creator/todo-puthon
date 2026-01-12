from datetime import date
from copy import deepcopy


def add_todo(data, title, desc):
    new_data = deepcopy(data)
    today = date.today()

    if new_data:
        max_id = max(int(key) for key in new_data.keys())
        new_id = str(max_id + 1)
    else:
        new_id = "0"

    new_data[new_id] = {
        "title": title,
        "description": desc,
        "added date": f"{today.day}.{today.month}.{today.year}",
        "completed": False
    }

    return new_data, True


def delete_todo(data, key_or_title):
    new_data = deepcopy(data)

    if key_or_title in new_data.keys():
        new_data.pop(key_or_title)
        return new_data, True

    for key, todo in list(new_data.items()):
        if todo.get("title", "").lower() == key_or_title.lower():
            new_data.pop(key)
            return new_data, True

    return new_data, False


def toggle_todo(data, key_or_title):
    new_data = deepcopy(data)

    if key_or_title in new_data:
        new_data[key_or_title]["completed"] ^= True
        return new_data, True

    for key, todo in new_data.items():
        if todo.get("title", "").lower() == key_or_title.lower():
            todo["completed"] ^= True
            return new_data, True

    return new_data, False


def get_all(data):
    return data.copy()
