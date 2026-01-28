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


class TodoUI:
    def __init__(self):
        self.manager = TodoManager()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_menu(self):
        print("\n=== TODO MANAGER ===")
        print("1. Add task")
        print("2. Show tasks")
        print("3. Toggle completed")
        print("4. Delete task")
        print("5. Search task")
        print("6. Clear all")
        print("0. Exit")

    def show_todos(self):
        todos = self.manager.get_all()

        if not todos:
            print("\nNo tasks")
            return

        print("\n=== TASKS ===")
        for task_id, task in todos.items():
            status = "✓" if task["completed"] else " "
            print(f"[{status}] ID: {task_id} | {task['title']}")
            print(f"    {task['description']} | {task['added date']}")

    def add_todo(self):
        title = input("\nTitle: ").strip()
        if not title:
            print("Title cannot be empty!")
            return

        desc = input("Description: ").strip()

        if self.manager.add(title, desc):
            self.manager.save()
            print("✓ Task added!")

    def toggle_todo(self):
        self.show_todos()
        if not self.manager.get_all():
            return

        task_id = input("\nID or title: ").strip()

        if self.manager.toggle(task_id):
            self.manager.save()
            print("✓ Status changed!")
        else:
            print("✗ Task not found")

    def delete_todo(self):
        self.show_todos()
        if not self.manager.get_all():
            return

        task_id = input("\nID or title: ").strip()
        confirm = input("Delete? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y']:
            if self.manager.delete(task_id):
                self.manager.save()
                print("✓ Task deleted!")
            else:
                print("✗ Task not found")

    def search_todo(self):
        if not self.manager.get_all():
            print("\nNo tasks")
            return

        query = input("\nSearch by ID or title: ").strip()
        result, found = self.manager.search(query)

        if found:
            print("\n=== SEARCH RESULT ===")
            if isinstance(result, dict):
                status = "✓" if result["completed"] else " "
                print(f"[{status}] ID: {query} | {result['title']}")
                print(f"    {result['description']} | {result['added date']}")
            else:
                task = self.manager.data[result]
                status = "✓" if task["completed"] else " "
                print(f"[{status}] ID: {result} | {task['title']}")
                print(f"    {task['description']} | {task['added date']}")
        else:
            print("✗ Task not found")

    def clear_all(self):
        if not self.manager.get_all():
            print("\nList is already empty")
            return

        confirm = input("\nDelete ALL tasks? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y']:
            self.manager.clear()
            self.manager.save()
            print("✓ All tasks deleted!")

    def run(self):
        while True:
            self.clear_screen()
            self.show_menu()

            choice = input("\nChoice: ").strip()

            if choice == "0":
                print("\nGoodbye!")
                break
            elif choice == "1":
                self.add_todo()
            elif choice == "2":
                self.show_todos()
            elif choice == "3":
                self.toggle_todo()
            elif choice == "4":
                self.delete_todo()
            elif choice == "5":
                self.search_todo()
            elif choice == "6":
                self.clear_all()
            else:
                print("Invalid choice!")

            if choice != "0":
                input("\n[Press Enter to continue]")


if __name__ == "__main__":
    app = TodoUI()
    app.run()
