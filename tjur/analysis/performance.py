class Performance():

    def calculate_pl(buy_price, sell_price):
        """
        Calculate margin out of gross margin.

        Returns:
        float
        """

        gross_profit = sell_price - buy_price
        margin = (gross_profit / sell_price) * 100

        return margin
