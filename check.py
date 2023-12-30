#!/usr/bin/env python3
"""Simple to-do app"""

import sys
import os
import logging
import json
from curses import wrapper

from check.task import Task
from check.ui import run_ui




def main(stdscr):
    """TODO"""

    try:
        # will create new file if it none is found or exists
        with open('tasks.json', 'r', encoding='utf-8') as json_file:
            loaded_tasks = json.load(json_file)
        tasks = [Task(task["title"], task["done"]) for task in loaded_tasks]
    except FileNotFoundError:  # if no json file exists or it is empty
        tasks = []
    except json.JSONDecodeError:
        tasks = []
    except Exception as e:
        print(f"An error occured when trying to open your tasks:\n{e}")
        sys.exit(1)

    run_ui(stdscr, tasks)

    # Save tasks to json file (new tasks only get saved to the
    # file once the programm is closed by pressing 'q')
    serialized_tasks = [task.__dict__ for task in tasks]
    with open('tasks.json', 'w', encoding='utf-8') as json_file:
        json.dump(serialized_tasks, json_file)  # overwrites!


wrapper(main)
