"""Simple to-do app"""

import json
import curses
from curses import wrapper

class Task:
    """Implemention of task object"""

    def __init__(self, title="Unnamed", done=False):
        """constructor of Task"""
        self.done = done
        self.title = title

    def display(self, stdscr, position):
        """displays the task given a y-Coordinate"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.addstr(position, 0, f"[{'x' if self.done else ' '}]",
                  curses.color_pair(1) if self.done else curses.A_NORMAL)
        # Use color pair 1 for 'x'
        stdscr.addstr(self.title)

    def check(self):
        """checks or unchecks a task"""
        self.done = not self.done

def add_task(stdscr, tasks):
    """Handles the prompt for adding a task and adds the task to a list of task objects"""
    input_string = ""
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height-1, 0, "Add task: ")

    while True:
        # Get user input
        key = stdscr.getch()

        # Check if Enter is pressed
        if key == 10:  # 10 is for Enter
            break #Promp ends when enter is pressed
        if key == curses.KEY_BACKSPACE:  # Handle backspace
            # Handle backspace (delete last character
            if len(input_string) > 0:
                input_string = input_string[:-1]
            else:
                return # if user presses Backspace when no input, the adding of a task is canceled
        if 32 <= key <= 126:  # ASCII values for printable characters
            input_string += chr(key)

        # Update the screen with the current input string
        stdscr.addstr(height-1, 10, " " * (width-11))  # Clear previous input
    stdscr.addstr(height-1, 0, " " * (width-1))
    tasks.append(Task() if not input_string else Task(input_string))
    #task gets default name 'unnamed' if user doesnt give a title

def main(stdscr):
    """Main function containing 'action loop' """


    #loads data form tasks.json file
    try:
        #will create new file if it none is found or exists
        with open('tasks.json', 'r', encoding='utf-8') as json_file:
            loaded_tasks = json.load(json_file)

        #parsing json objects into Task objects
        tasks = [Task(task["title"], task["done"]) for task in loaded_tasks]
    except: # if no json file exists or it is empty
        tasks = []

    selector_pos = 0 #sets the position of selector

    #main event loop

    while True:

        height, _ = stdscr.getmaxyx()

        for index, task in enumerate(tasks):
            task.display(stdscr, index)

        curses.curs_set(0) #Sets the real cursor invisible
        stdscr.chgat(selector_pos, 0, curses.A_REVERSE)
        #stdscr.refresh()

        key = stdscr.getch() #Listen for user input

        match key:
            case 32: #Press Space key to add task
                curses.curs_set(1) #Makes cursor visible
                add_task(stdscr, tasks)
            case 113: #Press 'q' to exit
                break
            case 107 | curses.KEY_UP: # k for going up
                if selector_pos > 0:
                    selector_pos -= 1
            case 106 | curses.KEY_DOWN: # j for going down
                if selector_pos < height-1:
                    selector_pos += 1
            case 100: # d for delete
                if tasks[selector_pos]:
                    del tasks[selector_pos]
            case 10: #Enter for marking tasks
                if tasks[selector_pos]:
                    tasks[selector_pos].check()

        stdscr.clear()

    #Save tasks to json file (new tasks only get saved to the
    #file once the programm is closed by pressing enter)

    serialized_tasks = [task.__dict__ for task in tasks] #serialization of loaded_tasks

    with open('tasks.json', 'w', encoding='utf-8') as json_file:
        json.dump(serialized_tasks, json_file) #saving new tasks by overwriting

wrapper(main)
