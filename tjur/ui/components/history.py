from datetime import datetime
from decimal import Decimal
from ui.drawing import Draw


class History:

    def __init__(self, exchange, symbol, history, minQty, curses, stdscr,
                 height, width, title):
        self.exchange = exchange
        self.symbol = symbol
        self.history = history
        self.minQty = minQty
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title
        self.tick_size = symbol['filters']['tick_size']
        self.quote_precision = symbol['filters']['quote_precision']
        self.min_qty = symbol['filters']['min_qty']
        if (self.minQty == 1):
            self.decToHide = 9
        else:
            self.decToHide = 2

    def draw(self):
        startY = int(self.height * 0.39)
        endX = int(self.width * 0.75)
        if ((self.width - endX) < 42):
            endX = self.width - 42
        distance = self.height - startY
        if (distance > 18):
            startY = self.height - 18

        self.stdscr.addstr(startY + 1, 4, 'time',
                           self.curses.color_pair(4))
        self.stdscr.addstr(startY + 1, 26, 'price',
                           self.curses.color_pair(4))
        self.stdscr.addstr(startY + 1, 39, 'qty',
                           self.curses.color_pair(4))
        self.stdscr.addstr(startY + 1, 50, 'total',
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
            history = self.history[i]
            self.stdscr.addstr((startY + 2) + i, 26,
                               self.format_price(history['price']),
                               self.curses.color_pair(6))
            self.stdscr.addstr((startY + 2) + i, 39,
                               self.format_qty(history['qty']),
                               self.curses.color_pair(6))
            self.stdscr.addstr((startY + 2) + i, 50, self.format_price(
                               Decimal(history['price'])
                               * Decimal(history['qty'])),
                               self.curses.color_pair(6))

        Draw(self.curses, self.stdscr, startY, self.height, 0, endX,
             self.title).draw_border()

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
