import storage
import logic

def main():
    data = storage.load_todos()

    while True:
        print("1. Show all todo")
        print("2. Add new todo")
        print("3. Delete todo")
        print("4. Toggle todo status")
        print("5. Clear all todo")
        print("6. Save and exit")
        print()

        try:
            action = int(input("Choice action: "))
        except ValueError:
            print("Please enter only numbers!")
            continue

        if action == 1:
            show_data = logic.get_all(data)
            for todo_id, todo in show_data.items():
                if todo["completed"]:
                    print(f"[{todo_id}] {todo["title"]} [✅]\ndesc: {todo["description"]} \nadded: {todo["added date"]}\n")
                else:
                    print(f"[{todo_id}] {todo["title"]} [❎]\ndesc: {todo["description"]} \nadded: {todo["added date"]}\n")

        elif action == 2:
            title = input("Title(not might be only numbers): ")
            while title.isdigit():
                print("Enter any characters except numbers")
                title = input("Title(not might be only numbers): ")
            desc = input("Description: ")
            data, operation_message = logic.add_todo(data, title, desc)
            if operation_message:
                print("✅== Successfully added ==✅\n")
            operation_message = None

        elif action == 3:
            key_or_title = input("Enter id or title: ")
            data, operation_message = logic.delete_todo(data, key_or_title)
            if operation_message:
                print("✅== Successfully deleted ==✅\n")
            else:
                print("⚠️== Todo not found ==⚠️\n")
            operation_message = None

        elif action == 4:
            key_or_title = input("Enter id or title: ")
            data, operation_message = logic.toggle_todo(data, key_or_title)
            if operation_message:
                print("✅== Successfully toggled ==✅\n")
            else:
                print("⚠️== Todo not found ==⚠️\n")
            operation_message = None

        elif action == 5:
            warning = input("Are you sure? (Enter \"yes\" for confirm): ")
            if warning.lower() == "yes":
                data = {}
                storage.clear_file()
                print("✅== All data successfully deleted ==✅\n")
            else:
                print("❎== Operation canceled ==❎")

        elif action == 6:
            storage.save_todos(data)
            break

        else:
            print("Invalid action")

if __name__ == "__main__":
    main()
