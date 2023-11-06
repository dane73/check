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

    def required_space(self, stdscr):
        """calculates how many lines EXTRA the task is going to need based on the text size and 
          window width"""
        _, width = stdscr.getmaxyx()
        return int(len(self.title)/(width-3))

    def display(self, stdscr, position):
        """displays the task given a y-Coordinate"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.addstr(position, 1, "[ ]")
        stdscr.addstr(position, 2, f"{'x' if self.done else ' '}",
                  curses.color_pair(1) if self.done else curses.A_NORMAL)
        # Use color pair 1 for 'x'
        if self.required_space(stdscr) < 1: #print one-line tasks
            stdscr.addstr(position, 4, self.title)
        else: #print multi line tasks
            _, width = stdscr.getmaxyx()
            for i in range(self.required_space(stdscr)+1): #only prints next to Bracket line
                stdscr.addstr(position + i, 4, self.title[(i*(width-4)):((i+1)*(width-4))])

    def check(self):
        """checks or unchecks a task"""
        self.done = not self.done

def user_prompt(stdscr, input_string, prompt):
    """prompts user given an input string"""
    height, _ = stdscr.getmaxyx()
    stdscr.addstr(height-1, 0, prompt)

    stdscr.addstr(height-1, len(prompt), input_string)

    cy, cx = stdscr.getyx()

    while True:

        height, width = stdscr.getmaxyx()

        # Get user input
        key = stdscr.getch()

        # Check if Enter is pressed
        if key == 10:  # 10 is for Enter
            break #Promp ends when enter is pressed
        if key == curses.KEY_BACKSPACE or key == 127:  # Handle Backspace
            #curses.KEY_BACKSPACE for linux terminal, 127 for macos
            # Handle backspace (delete last character
            if len(input_string) > 0:
                if cx < len(prompt) + 1:
                    continue
                index = cx - len(prompt) - 1
                input_string = input_string[:index] + input_string[index+1:]
                cx -= 1
            else:
                return None# if no input, backspace to cancel
        if 32 <= key <= 126:  # ASCII values for printable characters
            index = cx - len(prompt)
            input_string = input_string[:index] + chr(key) + input_string[index:]
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
            stdscr.addstr(height-1, len(prompt), " " * (width-len(prompt)-1))# Clear previous input
            stdscr.addstr(height-1, len(prompt), input_string)
            stdscr.move(cy, cx)
        except: #Will throw exception when resize during task-adding
            pass

    return input_string

def add_task(stdscr, tasks):
    """Handles the prompt for adding a task and adds the task to a list of task objects"""
    task_name = user_prompt(stdscr, "", "Add task: ")
    if task_name is not None:
        tasks.append(Task() if len(task_name) == 0 else Task(task_name))
    #task gets default name 'unnamed' if user doesnt give a title

def edit_task(stdscr, tasks, task):
    """editing of a task"""
    new_task_name = user_prompt(stdscr, tasks[task].title, "Edit task: ")
    if new_task_name is not None:
        tasks[task].title = "Unnamed" if len(new_task_name) == 0 else new_task_name

def print_welcome(stdscr, height, width):
    """Prints screen that occurs when no there are tasks"""
    stdscr.addstr(0, 1, " " * (width -1))
    for i in range(height):
        stdscr.addch(i, 0, '~')
    stdscr.addstr(int(height/2)-3, int(width/2)-13, "Check - a simple to-do app")
    stdscr.addstr(int(height/2)-1, int(width/2)-22, "Type:    q to exit")
    stdscr.addstr(int(height/2), int(width/2)-13, "j/k or <up>/<down> for moving selector")
    stdscr.addstr(int(height/2)+1, int(width/2)-13, "<space> to add task")
    stdscr.addstr(int(height/2)+2, int(width/2)-13, "<enter> to (un)check")
    stdscr.addstr(int(height/2)+3, int(width/2)-13, "d to delete task")
    stdscr.addstr(int(height/2)+4, int(width/2)-13, "e to edit task")
    curses.curs_set(0)

def main(stdscr):
    """Main function containing 'action loop' """



    #loads data form tasks.json file
    try:
        #will create new file if it none is found or exists
        with open('tasks.json', 'r', encoding='utf-8') as json_file:
            loaded_tasks = json.load(json_file)

        tasks = [Task(task["title"], task["done"]) for task in loaded_tasks]
    except: # if no json file exists or it is empty
        tasks = []

    selector_pos = 0

    if len(tasks) == 0:
        notask = True
    else:
        notask = False

    #main event loop
    while True:

        try: # try catch prevents program from crashing while squished

            height, width = stdscr.getmaxyx()

            if notask:
                print_welcome(stdscr, height, width)
            else: #print tasks
                offset = 0
                screen_selector_pos = list(range(len(tasks)))

                for index, task in enumerate(tasks):
                    try:
                        task.display(stdscr, index+offset)
                    except:
                        pass
                    screen_selector_pos[index] = offset + index
                    offset += task.required_space(stdscr)

                curses.curs_set(0) #Sets the real cursor invisible
                stdscr.chgat(screen_selector_pos[selector_pos],
                             4,
                             len(tasks[selector_pos].title),
                             curses.A_UNDERLINE)
                stdscr.addstr(screen_selector_pos[selector_pos], 0, ">")

            key = stdscr.getch() #Listen for user input

            match key:
                case 32: #Press Space key to add task
                    curses.curs_set(1) #Makes cursor visible
                    add_task(stdscr, tasks)
                    if notask:
                        notask = False
                case 113: #Press 'q' to exit
                    break
                case 107 | curses.KEY_UP: # k for going up
                    if notask:
                        continue
                    if selector_pos > 0:
                        selector_pos -= 1
                case 106 | curses.KEY_DOWN: # j for going down
                    if notask:
                        continue
                    if selector_pos < height-1 and selector_pos < len(tasks)-1:
                        selector_pos += 1
                case 101: # e for edit
                    if notask:
                        continue
                    curses.curs_set(1)
                    edit_task(stdscr, tasks, selector_pos)
                case 100: # d for delete
                    if notask:
                        continue
                    if tasks[selector_pos]:
                        del tasks[selector_pos]
                        if len(tasks) == 0:
                            notask = True
                            continue
                        if selector_pos is len(tasks): #handles case when last task gets deleted
                            selector_pos -= 1 #prevents selector from selecting nothing
                case 10: #Enter for marking tasks
                    if tasks[selector_pos]:
                        tasks[selector_pos].check()

            stdscr.clear()

        except:
            pass

    #Save tasks to json file (new tasks only get saved to the
    #file once the programm is closed by pressing enter)

    serialized_tasks = [task.__dict__ for task in tasks] #serialization of loaded_tasks

    with open('tasks.json', 'w', encoding='utf-8') as json_file:
        json.dump(serialized_tasks, json_file) #saving new tasks by overwriting

wrapper(main)
