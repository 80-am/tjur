from ui.drawing import Draw
from datetime import datetime


class History:

    def __init__(self, exchange, history, minQty, curses, stdscr, height,
                 width, title):
        self.exchange = exchange
        self.history = history
        self.minQty = minQty
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title
        if (self.minQty == 1):
            self.decToHide = 9
        else:
            self.decToHide = 2

    def draw(self):
        startY = int(self.height * 0.39)
        distance = self.height - startY
        if (distance > 18):
            startY = self.height - 18
        self.stdscr.addstr(startY + 1, 4, 'time',
                           self.curses.color_pair(4))
        self.stdscr.addstr(startY + 1, 26, 'qty',
                           self.curses.color_pair(4))
        self.stdscr.addstr(startY + 1, 39, 'price',
                           self.curses.color_pair(4))

        for i, trade in enumerate(self.history, 0):
            if (self.history[i]['isBuyer']):
                side = 'b'
                color = 3
            else:
                side = 's'
                color = 2
            self.stdscr.addstr((startY + 2) + i, 2, side,
                               self.curses.color_pair(color))

        for i, trade in enumerate(self.history, 0):
            ts = int(str(self.history[i]['time'])[:-3])
            self.stdscr.addstr((startY + 2) + i, 4, str(
                datetime.fromtimestamp(ts)),
                self.curses.color_pair(6))

        for i, trade in enumerate(self.history, 0):
            self.stdscr.addstr((startY + 2) + i, 26,
                               self.history[i]['qty'][:-self.decToHide],
                               self.curses.color_pair(6))

        for i, trade in enumerate(self.history, 0):
            self.stdscr.addstr((startY + 2) + i, 39,
                               self.history[i]['price'],
                               self.curses.color_pair(6))

        Draw(self.curses, self.stdscr, startY, self.height, 0,
             int(self.width - (self.width * 0.30)), self.title).draw_border()
