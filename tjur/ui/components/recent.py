from ui.drawing import Draw


class Recent:

    def __init__(self, exchange, symbol, curses, stdscr, height, width, title):
        self.exchange = exchange
        self.symbol = symbol
        self.curses = curses
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.title = title
        self.latest = 0

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
            self.stdscr.addstr(2 + i, startX + 2, self.recent[i]['price'],
                               self.curses.color_pair(color))
            self.stdscr.addstr(2 + i, startX + 15, self.recent[i]['qty'][:-9],
                               self.curses.color_pair(color))

        Draw(self.curses, self.stdscr, 0, self.height, startX, self.width,
             self.title).draw_border()

    def get_latest_price(self):
        self.latest = self.exchange.get_cur_avg_price(self.symbol)

    def get_recent_trades(self):
        self.recent = self.exchange.get_recent_trades(
            self.symbol, self.height - 3)
