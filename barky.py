"""
This module provides the presentation layer and can be consdired "the program."

This module facilitates an infinite loop that:
1. Clears the screen
2. Prints the menu options
    (A) Add a bookmark
    (B) List bookmarks by date
    (T) List bookmarks by title
    (D) Delete a bookmark
    (Q) Quit
3. Gets the user’s choice
    When chosen, use an Option class to match selection to command to
    1. Run the specified preparation step, if any.
    2. Pass the return value from the preparation step, if any, to the specified command’s execute method.
    3. Print the result of the execution. These are the success messages or bookmark results returned from the business logic.
4. Clears the screen and executes the command corresponding to the user’s choice
5. Waits for the user to review the result, pressing Enter when they’re done

Room to grow.  

This modular design, which separates concerns, provides opportunities for extensibility, making it possible to:
1. Add any new database manipulation methods you may need to database.py.
2. Add a command class that performs the business logic you need in commands.py.
3. Hook up the new command to a new menu option in barky.py.

"""

from commands import (
    AddBookmarkCommand,
    ListBookmarksCommand,
    DeleteBookmarkCommand,
    ImportGitHubStarsCommand,
    EditBookmarkCommand,
    QuitCommand,

)
from database import list_bookmarks
import os
import commands
import logging
from sqlalchemy import create_engine

logging.disable(logging.INFO)

engine = create_engine('sqlite:///bookmarks.db', echo=False)


class Option:
    def __init__(self, name, command, prep_call=None):
        self.name = name
        self.command = command
        self.prep_call = prep_call

    def choose(self):
        data = self.prep_call() if self.prep_call else None
        message = self.command.execute(data)
        print(message)

    def __str__(self):
        return self.name


def clear_screen():
    clear = "cls" if os.name == "nt" else "clear"
    os.system(clear)


def print_options(options):
    """
    Print the keyboard key for the user to enter to choose the option.
    Print the option text.
    Check if the user’s input matches an option and, if so, choose it.
    """
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")
    print()


def option_choice_is_valid(choice, options):
    return choice in options or choice.upper() in options


def get_option_choice(options):
    """
    Prompt the user to enter a choice.
    If the user’s choice matches one of those listed, call that option’s choose method.
    Otherwise, repeat.
    """
    choice = input("Choose an option: ")
    while not option_choice_is_valid(choice, options):
        print("Invalid choice")
        choice = input("Choose an option: ")
    return options[choice.upper()]


def get_user_input(label, required=True):
    value = input(f"{label}: ") or None
    while required and not value:
        value = input(f"{label}: ") or None
    return value


def get_new_bookmark_data():
    return {
        "title": get_user_input("Title"),
        "url": get_user_input("URL"),
        "notes": get_user_input("Notes", required=False),
    }


def get_bookmark_id_for_deletion():
    return get_user_input("Enter a bookmark ID to delete")


def get_github_import_options():
    return {
        "github_username": get_user_input("GitHub username"),
        "preserve_timestamps": get_user_input(
            "Preserve timestamps [Y/n]", required=False
        )
        in {"Y", "y", None},
    }


def get_new_bookmark_info():
    bookmark_id = get_user_input("Enter a bookmark ID to edit")
    field = get_user_input(
        "Choose a value to edit (title, URL, notes)").lower()
    new_value = get_user_input(f"Enter the new value for {field.capitalize()}")
    return {
        "id": bookmark_id,
        "update": {field: new_value},
    }


def loop():
    clear_screen()
    options = {
        "A": Option(
            "Add a bookmark",
            AddBookmarkCommand(),
            prep_call=get_new_bookmark_data,
        ),
        "B": Option("List bookmarks by date", ListBookmarksCommand(order_by="date_added")),
        "T": Option(
            "List bookmarks by title", ListBookmarksCommand(
                order_by="title")
        ),
        "E": Option(
            "Edit a bookmark",
            EditBookmarkCommand(),
            prep_call=get_new_bookmark_info,
        ),
        "D": Option(
            "Delete a bookmark",
            DeleteBookmarkCommand(),
            prep_call=get_bookmark_id_for_deletion,
        ),
        "G": Option(
            "Import GitHub stars",
            ImportGitHubStarsCommand(),
            prep_call=get_github_import_options,
        ),
        "Q": Option("Quit", QuitCommand()),
    }
    print_options(options)

    chosen_option = get_option_choice(options)
    clear_screen()
    if chosen_option.name == "List bookmarks by date" or chosen_option.name == "List bookmarks by title":
        bookmarks = list_bookmarks(
            order_by="date_added" if chosen_option.name == "List bookmarks by date" else "title")
        for bookmark in bookmarks:
            print(bookmark)
    else:
        chosen_option.choose()
    _ = input("Press ENTER to return to menu")


if __name__ == "__main__":
    commands.CreateBookmarksTableCommand().execute()

    while True:
        loop()
