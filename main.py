from datetime import date

todo_list = {}

def todo_add(text, description):
    today = date.today()

    todo = {
        text: {
            "description": description,
            "added date": f"{today.day}.{today.month}.{today.year}",
            "completed": False
        }
    }

    todo_list.update(todo)

def delete_todo(text):
    if text in todo_list:
        todo_list.pop(text)

def list_todo():
    return todo_list

def main():
    todo_add("test", "re")
    todo_add("fys", "kys")
    delete_todo("test")
    todo_add("55", "suck")
    print(list_todo())

if __name__ == "__main__":
    main()
