from ui.drawing import Draw


class Actions:

    def __init__(self, exchange, action, curses, stdscr, height, width, title):
        self.exchange = exchange
        self.action = action[::-1]
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title

    def draw(self):
        if (self.height < 30):
            return

        endY = self.height - 18
        endX = int(self.width * 0.75)
        if ((self.width - endX) < 42):
            endX = self.width - 42

        for i, val in enumerate(self.action):
            if (10 + i < endY + 1):
                self.stdscr.insstr(10 + i, 2, val, self.curses.color_pair(4))
            else:
                self.action.pop()

        Draw(self.curses, self.stdscr, 8, endY, 0, endX,
             self.title).draw_border()
