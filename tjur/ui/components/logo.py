from ui.drawing import Draw


class Logo:

    def __init__(self, symbol, curses, stdscr, title):
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.title = title
        self.titlePos = int(13 / len(self.symbol)) + 2

    def draw(self):
        self.stdscr.addstr(1, 3, '((...))', self.curses.color_pair(3))
        self.stdscr.addstr(2, 3, '(     )', self.curses.color_pair(3))
        self.stdscr.addstr(2, 4, ' o o ', self.curses.color_pair(2))
        self.stdscr.addstr(3, 3, ' \\   /', self.curses.color_pair(3))
        self.stdscr.addstr(4, 3, '  ^_^', self.curses.color_pair(3))
        self.stdscr.addstr(6, self.titlePos, self.symbol,
                           self.curses.color_pair(4))

        Draw(self.curses, self.stdscr, 0, 8, 0, 13, self.title).draw_border()
