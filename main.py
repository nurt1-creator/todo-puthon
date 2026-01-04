from datetime import date
import os
import json

FILE_NAME = "todo.json"
todo_list = {}

if not os.path.isfile(FILE_NAME):
    with open(FILE_NAME, "w") as file:
        pass

def todo_load():
    global todo_list
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            todo_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
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

def change_state(text):
    if text in todo_list:
        todo_list[text]["completed"] = not todo_list[text]["completed"]
        todo_update()

def list_todo():
    todo_load()
    return todo_list

def delete_all():
    with open(FILE_NAME, "w") as file:
        pass

def ui():
    def menu():
        print("1.Show all todo")
        print("2.Add todo")
        print("3.Delete todo")
        print("4.Change state")
        print("5.Delete all todo(unrecomended)")

    menu()
    select = int(input())
    while 1 <= select and 5 >= select:
        if select == 1:
            print(list_todo())
        elif select == 2:
            text = input("Enter todo title: ")
            description = input("Enter todo description: ")
            todo_add(text, description)
        elif select == 3:
            text = input("Enter todo title: ")
        elif select == 4:
            text = input("Enter todo title: ")
        elif select == 5:
            sure = False
            answer = input("Are you sure?(yes/no)")
            if answer.lower() == "yes":
                delete_all()
            elif answer.lower() == "no":
                print("canceled")
            else:
                print("wrong")
        menu()
        select = int(input())

def main():
    while 1:
        ui()

if __name__ == "__main__":
    main()
