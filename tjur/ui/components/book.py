import itertools
from decimal import Decimal
from ui.drawing import Draw


class Book:

    def __init__(self, socket, symbol, curses, stdscr,
                 height, width, title):
        self.socket = socket
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title
        self.tick_size = symbol['filters']['tick_size']
        self.quote_precision = symbol['filters']['quote_precision']
        self.min_qty = symbol['filters']['min_qty']
        self.mid = int(self.height / 2) + 1

    def draw(self):
        self.get_orders()

        startX = int(self.width * 0.75)
        if ((self.width - startX) < 42):
            startX = self.width - 42

        self.stdscr.addstr(1, startX + 2, 'price', self.curses.color_pair(4))
        self.stdscr.addstr(1, startX + 15, 'qty', self.curses.color_pair(4))
        self.stdscr.addstr(1, startX + 26, 'total', self.curses.color_pair(4))

        for i, trade in enumerate(self.asks):
            self.stdscr.addstr(2 + i, startX + 2, self.format_price(
                self.asks[i][0]),
                self.curses.color_pair(2))
            self.stdscr.addstr(2 + i, startX + 15, self.format_qty(
                self.asks[i][1]),
                self.curses.color_pair(2))
            self.stdscr.addstr(2 + i, startX + 26, self.format_price(
                Decimal(self.asks[i][0])
                * Decimal(self.asks[i][1])),
                self.curses.color_pair(2))

        for i, trade in enumerate(self.bids):
            self.stdscr.addstr(self.mid + i, startX + 2, self.format_price(
                self.bids[i][0]),
                self.curses.color_pair(3))
            self.stdscr.addstr(self.mid + i, startX + 15, self.format_qty(
                self.bids[i][1]),
                self.curses.color_pair(3))
            self.stdscr.addstr(self.mid + i, startX + 26, self.format_price(
                Decimal(self.bids[i][0])
                * Decimal(self.bids[i][1])),
                self.curses.color_pair(3))

        Draw(self.curses, self.stdscr, 0, self.height, startX, self.width,
             self.title).draw_border()

    def get_orders(self):
        self.asks = list(itertools.islice(self.socket.get_book().get('asks'),
                                          self.mid - 3))
        self.bids = list(itertools.islice(self.socket.get_book().get('bids'),
                                          self.mid - 3))

    def format_qty(self, val):
        if (self.min_qty < 1):
            return val[:self.quote_precision]
        else:
            return val.split(".")[0]

    def format_price(self, val):
        if (self.tick_size <= 8):
            return str(Decimal(val).quantize(Decimal(10) ** -self.tick_size))
        else:
            return str(val)
