from datetime import date
import json

FILE_NAME = "todo.json"

with open(FILE_NAME, "w") as file:
    pass

with open(FILE_NAME, "r") as file:
    if file.read():
        todo_list = json.load(file)
    else:
        todo_list = {}

def todo_update():
    with open(FILE_NAME, "w") as file:
        json.dump(todo_list, file, indent=4)

def todo_add(text, description):
    today = date.today()

    if text not in todo_list:
        todo = {
            text: {
                "description": description,
                "added date": f"{today.day}.{today.month}.{today.year}",
                "completed": False
            }
        }

        todo_list.update(todo)
        todo_update()

def delete_todo(text):
    if text in todo_list:
        todo_list.pop(text)
        todo_update()

def list_todo():
    return todo_list

def main():
    todo_add("test", "re")
    todo_add("fys", "kys")
    delete_todo("test")
    todo_add("55", "suck")
    todo_add("55", "nah")
    print(list_todo())

if __name__ == "__main__":
    main()
