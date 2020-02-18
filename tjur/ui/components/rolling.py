from decimal import Decimal
from ui.drawing import Draw


class Rolling:

    def __init__(self, socket, symbol, symbol2, minQty, curses,
                 stdscr, width, title):
        self.socket = socket
        self.symbol = symbol
        self.symbol2 = symbol2
        self.minQty = minQty
        self.curses = curses
        self.stdscr = stdscr
        self.width = width
        self.title = title
        self.prev = 0

        if (self.minQty > 0):
            self.decimals = 9
        else:
            self.decimals = 0

    def draw(self):
        self.get_rolling()
        if (self.prev < Decimal(self.rolling['c'])):
            latestColor = 3
        else:
            latestColor = 2

        if (float(self.rolling['p']) > 0):
            color = 3
            operator = '+'
        else:
            color = 2
            operator = ''
        self.stdscr.addstr(1, 11, 'change', self.curses.color_pair(4))
        self.stdscr.addstr(2, 11, self.rolling['p'],
                           self.curses.color_pair(color))
        self.stdscr.addstr(3, 11, operator
                           + self.rolling['P'][:-1] + '%',
                           self.curses.color_pair(color))
        self.stdscr.addstr(1, 24, 'high', self.curses.color_pair(4))
        self.stdscr.addstr(2, 24, self.rolling['h'],
                           self.curses.color_pair(6))
        self.stdscr.addstr(1, 36, 'low', self.curses.color_pair(4))
        self.stdscr.addstr(2, 36, self.rolling['l'],
                           self.curses.color_pair(6))
        if (self.width > 95):
            self.stdscr.addstr(1, 48, 'volume', self.curses.color_pair(4))
            self.stdscr.addstr(2, 48, self.rolling['q'][:-self.decimals]
                               + ' ' + self.symbol2, self.curses.color_pair(6))

        self.stdscr.addstr(5, 11, 'last price', self.curses.color_pair(4))
        self.stdscr.addstr(6, 11, self.rolling['c'],
                           self.curses.color_pair(latestColor))
        Draw(self.curses, self.stdscr, 0, 8, 9, int(
             self.width - (self.width * 0.30)), self.title).draw_border()

    def get_rolling(self):
        df = self.socket.get_rolling()
        if (len(df.index) <= 1):
            self.rolling = df.iloc[0]
        else:
            self.rolling = df.iloc[1]
            self.prev = Decimal(df.iloc[0]['c'])
