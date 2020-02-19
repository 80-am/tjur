from decimal import Decimal
from ui.drawing import Draw


class Rolling:

    def __init__(self, socket, symbol, curses, stdscr, width, title):
        self.socket = socket
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.width = width
        self.title = title
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
        self.stdscr.addstr(1, 11, 'change', self.curses.color_pair(4))
        self.stdscr.addstr(2, 11, self.format_price(self.rolling['p']),
                           self.curses.color_pair(color))
        self.stdscr.addstr(3, 11, operator
                           + self.rolling['P'][:-1] + '%',
                           self.curses.color_pair(color))
        self.stdscr.addstr(1, 24, 'high', self.curses.color_pair(4))
        self.stdscr.addstr(2, 24, self.format_price(self.rolling['h']),
                           self.curses.color_pair(6))
        self.stdscr.addstr(1, 36, 'low', self.curses.color_pair(4))
        self.stdscr.addstr(2, 36, self.format_price(self.rolling['l']),
                           self.curses.color_pair(6))
        if (self.width > 95):
            self.stdscr.addstr(1, 48, 'volume', self.curses.color_pair(4))
            self.stdscr.addstr(2, 48, self.rolling['q'].rpartition('.')[0]
                               + ' ' + self.symbol[1]['symbol'],
                               self.curses.color_pair(6))

        self.stdscr.addstr(5, 11, 'last price', self.curses.color_pair(4))
        self.stdscr.addstr(6, 11, self.format_price(self.rolling['c']),
                           self.curses.color_pair(latestColor))
        Draw(self.curses, self.stdscr, 0, 8, 9, int(
             self.width - (self.width * 0.30)), self.title).draw_border()

    def format_price(self, val):
        if (self.tick_size < 8):
            return str(Decimal(val).quantize(Decimal(10) ** -self.tick_size))
        else:
            return str(val)

    def get_rolling(self):
        df = self.socket.get_rolling()
        if (len(df.index) <= 1):
            self.rolling = df.iloc[0]
        else:
            self.rolling = df.iloc[1]
            self.prev = Decimal(df.iloc[0]['c'])
