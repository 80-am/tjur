from ui.drawing import Draw


class Logo:

    def __init__(self, symbol, curses, stdscr, title):
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.title = title

    def draw(self):
        self.stdscr.addstr(1, 1, '((...))', self.curses.color_pair(3))
        self.stdscr.addstr(2, 1, '(     )', self.curses.color_pair(3))
        self.stdscr.addstr(2, 2, ' o o ', self.curses.color_pair(2))
        self.stdscr.addstr(3, 1, ' \\   /', self.curses.color_pair(3))
        self.stdscr.addstr(4, 1, '  ^_^', self.curses.color_pair(3))
        self.stdscr.addstr(6, 1, self.symbol, self.curses.color_pair(4))

        Draw(self.curses, self.stdscr, 0, 8, 0, 9, self.title).draw_border()
