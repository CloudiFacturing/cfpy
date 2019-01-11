# -*- coding: future_fstrings -*-
import sys
import os
import getpass
from builtins import input


def query_password(prompt, min_length=12):
    while True:
        password = getpass.getpass(prompt)
        if len(password) < min_length:
            print(f"Password must be at least {min_length} characters long")
        else:
            return password


def query_int(question, default=None):
    if default is None:
        prompt = " "
    elif isinstance(default, int):
        prompt = f" [{default}] "
    else:
        raise ValueError(f"Invalid default answer {default}")

    while True:
        sys.stdout.write(question + prompt)
        choice = input()
        if default is not None and choice == '':
            return default
        else:
            try:
                value = int(choice)
            except ValueError:
                sys.stdout.write("Please enter an integer\n")
                continue
            return value


def query_filepath(question):
    prompt = " "
    while True:
        sys.stdout.write(question + prompt)
        choice = input()
        if not os.path.isfile(choice):
            print("Please enter a valid path to a file")
            continue
        else:
            return choice


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return the answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
