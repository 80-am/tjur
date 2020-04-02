from decimal import Decimal
from ui.drawing import Draw


class Rolling:

    def __init__(self, socket, symbol, curses, stdscr, height, width, title):
        self.socket = socket
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.height = int(height / 2)
        self.width = int(width - (width * 0.25))
        self.title = title
        self.full_width = width
        self.prev = 0
        self.tick_size = symbol['filters']['tick_size']

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
        endX = int(self.full_width * 0.75)
        if ((self.full_width - endX) < 42):
            endX = self.full_width - 42

        self.stdscr.addstr(1, 15, 'change', self.curses.color_pair(4))
        self.stdscr.addstr(2, 15, self.format_price(self.rolling['p']),
                           self.curses.color_pair(color))
        self.stdscr.addstr(3, 15, operator
                           + self.rolling['P'][:-1] + '%',
                           self.curses.color_pair(color))
        self.stdscr.addstr(1, 28, 'high', self.curses.color_pair(4))
        self.stdscr.addstr(2, 28, self.format_price(self.rolling['h']),
                           self.curses.color_pair(6))
        self.stdscr.addstr(1, 40, 'low', self.curses.color_pair(4))
        self.stdscr.addstr(2, 40, self.format_price(self.rolling['l']),
                           self.curses.color_pair(6))
        if (self.width > 80):
            self.stdscr.addstr(1, 51, 'volume', self.curses.color_pair(4))
            self.stdscr.addstr(2, 51, self.rolling['q'].rpartition('.')[0]
                               + ' ' + self.symbol[1]['symbol'],
                               self.curses.color_pair(6))

        self.stdscr.addstr(5, 15, 'last price', self.curses.color_pair(4))
        self.stdscr.addstr(6, 15, self.format_price(self.rolling['c']),
                           self.curses.color_pair(latestColor))

        for i in range(endX + 1, self.full_width - 1):
            self.stdscr.addstr(self.height, i, ' ', self.curses.color_pair(1))
        self.stdscr.addstr(self.height, endX + 2,
                           self.format_price(self.rolling['c']),
                           self.curses.color_pair(1))

        Draw(self.curses, self.stdscr, 0, 8, 13, endX,
             self.title).draw_border()

    def format_price(self, val):
        if (self.tick_size < 8):
            return str(Decimal(val).quantize(Decimal(10) ** -self.tick_size))
        else:
            return str(val)

    def get_rolling(self):
        df = self.socket.get_ticker()
        if (len(df.index) <= 1):
            self.rolling = df.iloc[0]
        else:
            self.rolling = df.iloc[1]
            self.prev = Decimal(df.iloc[0]['c'])
        self.len = str(len(df.index))
