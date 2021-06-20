import logging
import time
from abc import ABC, abstractmethod

import currency
import mplfinance as mplf
from PIL import Image, ImageDraw
from util import util

from yaticker import yaticker


class Dashboard(ABC):
    @abstractmethod
    def __init__(self, width, height, dpi):
        self._width = width
        self._height = height
        self._dpi = dpi

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def dpi(self):
        return self._dpi

    @abstractmethod
    def display_image(self, img):
        pass

    def display_message(self, message):
        try:
            image = util.empty_image(width=self.width, height=self.height)
            draw = ImageDraw.Draw(image)
            draw.text((95, 15), str(time.strftime("%-H:%M %p, %-d %b %Y")), fill=0)
            util.write_wrapped_lines(image, message)
            self.display_image(image)
        except Exception as e:
            logging.info(f"Exception: {e}")

    @staticmethod
    def stock_graph(data, height=116, width=264, dpi=117, filename="candle.png"):
        fig_size = (width / dpi, height / dpi)
        custom_rc = {
            "font.size": 8,
            # This removes the frames from the axes
            "axes.spines.left": False,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.spines.bottom": False,
            # lets try to have the size behave
            "figure.figsize": fig_size,
            "axes.xmargin": 0,
            "axes.ymargin": 0,
        }
        style_settings = mplf.make_mpf_style(
            base_mpf_style="binance",
            rc=custom_rc,
            gridstyle="",
        )

        fig, _ = mplf.plot(
            data,
            figsize=fig_size,
            type="line",
            style=style_settings,
            tight_layout=True,
            # we make the lines thinner
            # see https://github.com/matplotlib/mplfinance/blob/master/examples/widths.ipynb
            update_width_config=dict(line_width=1),
            # let's rotate the dates so that they are not angled
            xrotation=0,
            datetime_format="%H:%M",
            ylabel="",
            scale_padding=0.2,
            returnfig=True,
        )
        util.set_size(fig, fig_size)
        fig.savefig(fname=filename, dpi=dpi, bbox_inches="tight")
        return filename

    def display_stock(self, stock="amc", period: str = "5d", interval: str = "1h"):
        """
        Displays the stock data, the stock last price (at the desired coin/fiat)
        :param stock: symbol of the stock to display
        :param period: time period to display
        :param interval: granularity of the data
        :return:
        """
        stock_info = yaticker.YaTicker.get_ticker_info(stock)
        data = yaticker.YaTicker.get_ticker_data(
            ticker=stock, period=period, interval=interval
        )

        # we clear the image first
        image = util.empty_image(width=self.width, height=self.height)
        ImageDraw.Draw(image)

        # we draw the stock graph
        stock_image = Image.open(self.stock_graph(data))
        image.paste(stock_image, (0, 0))

        # we draw the latest stock's price
        latest_price = data["Close"][-1]
        closing_str = f"{currency.symbol('USD')}{util.number_to_string(latest_price)}"
        stock_price_font_size = 48
        y_offset = ((self.height - stock_price_font_size) / 2) - 12
        x_offset = -29
        util.place_centered_text(
            img=image,
            text=closing_str,
            font_size=stock_price_font_size,
            x_offset=x_offset,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

        # we put the stock name at the bottom right of the graph
        symbol_font_size = 20
        y_offset = self.height - stock_price_font_size
        util.place_text_right(
            img=image,
            text=stock.upper(),
            font_size=symbol_font_size,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

        # we add the diff vs last trading window
        previous_close = stock_info.get("previousClose")
        if previous_close is not None:
            delta_str = f"{(latest_price - previous_close):+.2g}"
            delta_percent = util.get_percentage_diff(latest_price, previous_close)
            diff_str = f"{delta_str} ({delta_percent:+.2f}%)"

            diff_font_size = 10
            y_offset = self.height - stock_price_font_size + symbol_font_size
            util.place_text_right(
                img=image,
                text=diff_str,
                font_size=diff_font_size,
                y_offset=y_offset,
                font_name="Roboto-Medium",
            )

        # date of last ticker data at the bottom
        last_data_time = (
            data.index[-1].tz_convert("Asia/Singapore").strftime("%-H:%M %p, %-d %b %Y")
        )

        last_date_font_size = 10
        y_offset = (self.height - last_date_font_size) / 2
        util.place_centered_text(
            img=image,
            text=last_data_time,
            font_size=last_date_font_size,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

        # we display the final image
        self.display_image(image)
