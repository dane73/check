"""
TODO
"""
import curses


class Task:
    """

    Attributes
        title: str
        done: bool
    """

    def __init__(self, title="Unnamed", done=False):
        """

        Parameters
            title: str
            - default: "Unnamed"
            done: bool
            - default: false
        """
        self.done = done
        self.title = title

    def required_space(self, width):
        """
        calculates how many lines EXTRA the task is going to need based on the
        text size and window width

        Parameters
            stdscr: curses window
        """

        return int(len(self.title)/(width-3))

    def display(self, stdscr, position, width):
        """displays the task given a y-Coordinate

        Parameters
            stdscr: curses window
            position: int
        """
        stdscr.addstr(position, 1, "[ ]")
        stdscr.addstr(position, 2, f"{'x' if self.done else ' '}",
                      curses.color_pair(1) if self.done else curses.A_NORMAL)
        # Use color pair 1 for 'x'
        if self.required_space(width) < 1:  # print one-line tasks
            stdscr.addstr(position, 4, self.title)
        else:  # print multi line tasks
            # only prints next to Bracket line
            for i in range(self.required_space(width)+1):
                stdscr.addstr(position + i, 4,
                              self.title[(i*(width-4)):((i+1)*(width-4))])

    def check(self):
        """checks or unchecks a task"""
        self.done = not self.done
