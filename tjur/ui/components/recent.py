from decimal import Decimal
from ui.drawing import Draw


class Recent:

    def __init__(self, socket, exchange, symbol, curses, stdscr, height, width,
                 title):
        self.exchange = exchange
        self.socket = socket
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title
        self.latest = 0
        self.tick_size = symbol['filters']['tick_size']
        self.quote_precision = symbol['filters']['quote_precision']
        self.min_qty = symbol['filters']['min_qty']

    def draw(self):
        self.get_recent_trades()
        self.get_latest_price()

        startX = int(self.width * 0.70)
        self.stdscr.addstr(1, startX + 2, 'price', self.curses.color_pair(4))
        self.stdscr.addstr(1, startX + 15, 'qty', self.curses.color_pair(4))
        for i, trade in enumerate(self.recent):
            if (float(self.recent[i]['price']) >= self.latest):
                color = 3
            else:
                color = 2
            self.stdscr.addstr(2 + i, startX + 2, self.format_price(
                               self.recent[i]['price']),
                               self.curses.color_pair(color))
            self.stdscr.addstr(2 + i, startX + 15, self.format_qty(
                               self.recent[i]['qty']),
                               self.curses.color_pair(color))

        Draw(self.curses, self.stdscr, 0, self.height, startX, self.width,
             self.title).draw_border()

    def get_latest_price(self):
        df = self.socket.get_rolling()
        self.latest = Decimal(df.iloc[0]['c'])

    def get_recent_trades(self):
        self.recent = self.exchange.get_recent_trades(
            self.symbol['symbol'], self.height - 3)

    def format_qty(self, val):
        if (self.min_qty < 1):
            return val[:self.quote_precision]
        else:
            return val.split(".")[0]

    def format_price(self, val):
        if (self.tick_size < 8):
            return str(Decimal(val).quantize(Decimal(10) ** -self.tick_size))
        else:
            return str(val)
