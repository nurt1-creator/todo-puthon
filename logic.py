from datetime import date
from copy import deepcopy
import json
import os

DEFAULT_FILE = "todo.json"


class TodoManager:
    def __init__(self, filename=DEFAULT_FILE):
        self.filename = filename
        self.data = self.load()

    def load(self) -> dict:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def add(self, title, desc):
        new_data = deepcopy(self.data)
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

        self.data = new_data
        return True

    def delete(self, key_or_title):
        new_data = deepcopy(self.data)

        if key_or_title in new_data.keys():
            new_data.pop(key_or_title)
            self.data = new_data
            return True

        for key, todo in list(new_data.items()):
            if todo.get("title", "").lower() == key_or_title.lower():
                new_data.pop(key)
                self.data = new_data
                return True

        self.data = new_data
        return False

    def toggle(self, key_or_title):
        new_data = deepcopy(self.data)

        if key_or_title in new_data:
            new_data[key_or_title]["completed"] = not new_data[key_or_title]["completed"]
            self.data = new_data
            return True

        for key, todo in new_data.items():
            if todo.get("title", "").lower() == key_or_title.lower():
                todo["completed"] = not todo["completed"]
                self.data = new_data
                return True

        self.data = new_data
        return False

    def search(self, key_or_title):
        founded_todo = {}

        if key_or_title in self.data:
            founded_todo = self.data[key_or_title]
            return founded_todo, True

        for key, todo in self.data.items():
            if todo.get("title", "").lower().startswith(key_or_title.lower()):
                founded_todo = {key: todo}

        if founded_todo:
            return founded_todo, True

        return None, False

    def get_all(self):
        return deepcopy(self.data)

    def clear(self):
        self.data = {}





if __name__ == "__main__":
    todo = TodoManager()
    todo.add("task", "test task")
    todo.save()
