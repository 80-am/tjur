class Draw:

    def __init__(self, curses, stdscr, startY, endY, startX, endX, title):
        self.curses = curses
        self.stdscr = stdscr
        self.startY = startY
        self.endY = endY
        self.startX = startX
        self.endX = endX
        self.title = title

    def draw_border(self):
        self.draw_vertical(self.startY, self.endY, self.startX, ['┌', '└'],
                           self.curses.color_pair(7))

        self.draw_horizontal(self.startX + 1, self.endX - 1, self.startY,
                             self.curses.color_pair(7))
        self.draw_horizontal(self.startX + 1, self.endX - 1, self.endY - 1,
                             self.curses.color_pair(7))
        self.draw_vertical(self.startY, self.endY, self.endX - 1, ['┐', '┘'],
                           self.curses.color_pair(7))
        self.stdscr.addstr(self.startY, self.startX + 2, self.title,
                           self.curses.color_pair(8))

    def draw_horizontal(self, startX, endX, y, color):
        for i in range(startX, endX):
            self.stdscr.addstr(y, i, '─', color)

    def draw_vertical(self, startY, endY, x, corners, color):
        self.stdscr.insstr(startY, x, corners[0], color)
        for i in range(startY + 1, endY - 1):
            self.stdscr.addstr(i, x, '│', color)
        self.stdscr.insstr(endY - 1, x, corners[1], color)
