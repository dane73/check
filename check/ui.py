"""
TODO
"""

import curses
import os
import logging

from check.task import Task


def setup_logging():
    home_dir = os.path.expanduser('~/code/check')
    log_path = os.path.join(home_dir, 'check.log')

    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def user_prompt(screen, input_string, prompt, height):
    """prompts user given an input string"""
    curses.curs_set(1)
    screen.addstr(height-1, 0, prompt)

    screen.addstr(height-1, len(prompt), input_string)

    cy, cx = screen.getyx()  # cursor position

    while True:

        height, width = screen.getmaxyx()

        # Get user input
        key = screen.getch()

        if key == 10:  # 10 is for Enter
            break  # Promp ends when enter is pressed

        if key == curses.KEY_BACKSPACE or key == 127:  # Handle Backspace
            # curses.KEY_BACKSPACE for linux terminal, 127 for macos

            if len(input_string) == 0:
                return None

            if cx < len(prompt) + 1:  # check bound for cursor at end of prompt
                continue

            index = cx - len(prompt) - 1
            input_string = input_string[:index] + input_string[index+1:]
            cx -= 1

        if 32 <= key <= 126:
            index = cx - len(prompt)
            input_string = input_string[:index] + \
                chr(key) + input_string[index:]
            cx += 1

        if curses.KEY_LEFT == key:
            if cx < len(prompt)+1:
                continue
            cx -= 1

        if curses.KEY_RIGHT == key:
            if cx > len(prompt + input_string)-1:
                continue
            cx += 1

        # Update the screen with the current input string
        try:
            screen.addstr(height-1, len(prompt), " " *
                          (width-len(prompt)-1))  # Clear previous input
            screen.addstr(height-1, len(prompt), input_string)
            screen.move(cy, cx)
        except curses.error:
            # Will throw exception when resize during task-adding
            pass

    return input_string


def add_task(screen, tasks, height):
    """
    Handles the prompt for adding a
    task and adds the task to a list of task objects
    """
    task_name = user_prompt(screen, "", "Add task: ", height)
    if task_name is not None:
        tasks.append(Task() if len(task_name) == 0 else Task(task_name))


def edit_task(screen, tasks, task, height):
    """editing of a task"""
    new_task_name = user_prompt(
        screen, tasks[task].title, "Edit task: ", height)
    if new_task_name is not None:
        tasks[task].title = "Unnamed" if len(
            new_task_name) == 0 else new_task_name


def print_welcome(screen, height, width):
    """Prints screen that occurs when no tasks are there"""
    screen.addstr(0, 1, " " * (width - 1))
    for i in range(height):
        screen.addch(i, 0, '~')
    screen.addstr(int(height/2)-3, int(width/2) -
                  13, "Check - a simple to-do app")
    screen.addstr(int(height/2)-1, int(width/2)-22, "Type:    q to exit")
    screen.addstr(int(height/2), int(width/2)-13,
                  "j/k or <up>/<down> for moving selector")
    screen.addstr(int(height/2)+1, int(width/2)-13, "<space> to add task")
    screen.addstr(int(height/2)+2, int(width/2)-13, "<enter> to (un)check")
    screen.addstr(int(height/2)+3, int(width/2)-13, "d to delete task")
    screen.addstr(int(height/2)+4, int(width/2)-13, "e to edit task")
    curses.curs_set(0)
    screen.refresh()


def print_tasks(screen, tasks, selector_pos, height, width,
                term_height, term_width, scroll):

    lines_needed_for_tasks = get_tasklength(tasks, width)

    if lines_needed_for_tasks > height:
        screen = curses.newpad(lines_needed_for_tasks+10, width)

    offset = 0
    screen_selector_pos = list(range(len(tasks)))

    for index, task in enumerate(tasks):
        try:
            task.display(screen, index+offset, width)
        except curses.error:
            pass
        screen_selector_pos[index] = offset + index
        offset += task.required_space(width)

    curses.curs_set(0)  # Sets the real cursor invisible
    screen.chgat(screen_selector_pos[selector_pos],
                 4,
                 len(tasks[selector_pos].title),
                 curses.A_UNDERLINE)
    screen.addstr(screen_selector_pos[selector_pos], 0, ">")
    screen.refresh(scroll, 0, 0, 0, term_height-1, term_width-1)


def get_tasklength(tasks, width):
    """
    Calculates the number of lines that the tasks are going
    to take up based on the current window width
    """
    task_length = 0

    for task in tasks:
        task_length += 1 + task.required_space(width)

    return task_length


def run_ui(stdscr, tasks):

    setup_logging()
    logger = logging.getLogger(__name__)

    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)

    selector_pos = 0

    notask = len(tasks) == 0

    scroll = 0

    height, width = stdscr.getmaxyx()

    task_length = get_tasklength(tasks, width)

    pad = curses.newpad(task_length+10, width)

    # main event loop
    while True:

        height, width = stdscr.getmaxyx()
        pad_height, pad_width = pad.getmaxyx()

        stdscr.refresh()

        if notask:
            print_welcome(stdscr, height, width)
        else:
            print_tasks(pad, tasks, selector_pos,
                        pad_height, pad_width, height, width, scroll)

        key = stdscr.getch()

        match key:
            case 32:  # Press Space key to add task
                add_task(stdscr, tasks, height)
                if notask:
                    notask = False
            case 113:  # Press 'q' to exit
                break
            case 107 | curses.KEY_UP:  # k for going up
                if notask:
                    continue
                if selector_pos > 0:
                    selector_pos -= 1
            case 106 | curses.KEY_DOWN:  # j for going down
                if notask:
                    continue  # NOTE: pass or continue?
                if selector_pos < height-1 and selector_pos < len(tasks)-1:
                    selector_pos += 1
            case 101:  # e for edit
                if notask:
                    continue
                edit_task(stdscr, tasks, selector_pos, height)
            case 100:  # d for delete
                if notask:
                    continue
                if tasks[selector_pos]:
                    del tasks[selector_pos]
                    if len(tasks) == 0:
                        notask = True
                        continue
                    # TODO: handle case when actual last tasks gets deleted
                    if selector_pos is len(tasks):
                        # prevents selector from selecting nothing
                        selector_pos -= 1
            case 10:  # Enter for marking tasks
                if tasks[selector_pos]:
                    tasks[selector_pos].check()
            case 112:  # p
                if scroll == 0:
                    continue
                scroll -= 1
            case 110:  # n
                if scroll == get_tasklength(tasks, pad_width)-1:
                    continue
                scroll += 1

        pad.clear()
        stdscr.clear()
