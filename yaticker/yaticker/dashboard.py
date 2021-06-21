import inspect
import logging
import sched
import time
from abc import ABC, abstractmethod
from itertools import cycle

import currency
import mplfinance as mplf
import yaml
from PIL import Image, ImageDraw
from util import util

from yaticker import yaticker

matplotlib_logger = logging.getLogger("matplotlib")
matplotlib_logger.setLevel(logging.ERROR)


class Dashboard(ABC):
    @abstractmethod
    def __init__(self, width, height, dpi, config_file=None):
        self._width = width
        self._height = height
        self._dpi = dpi
        self._config = Dashboard.load_config(config_file)
        self._cycle = self._config.get("cycle", True)
        self._update_frequency = self._config.get("updatefrequency", 300)
        self._show_volume = self._config.get("showvolume", False)
        self._period = self._config.get("period", "5d")
        self._watchlist = self._config.get("watchlist", ["AMZN", "FB", "APPL"])
        self._watchlist_cycle = cycle(self._watchlist)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def dpi(self):
        return self._dpi

    @property
    def cycle(self):
        return self._cycle

    @property
    def update_frequency(self):
        return self._update_frequency

    @property
    def show_volume(self):
        return self._show_volume

    @property
    def period(self):
        return self._period

    @property
    def watchlist(self):
        return self._watchlist

    @abstractmethod
    def display_image(self, img):
        pass

    @staticmethod
    def load_config(config_file):
        config = {}
        try:
            with open(config_file) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            logging.debug(f"Unable to read config file {config_file}.")
            logging.error(e, exc_info=True)
        return config

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
    def stock_graph(
        data, show_volume=False, height=116, width=264, dpi=117, filename="candle.png"
    ):
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

        time_period = data.index[-1] - data.index[0]
        if time_period.days > 1:
            x_axis_datetime_format = "%-d/%-m"
        else:
            x_axis_datetime_format = "%H:%M"
        fig, _ = mplf.plot(
            data,
            figsize=fig_size,
            type="line",
            style=style_settings,
            tight_layout=True,
            volume=show_volume,
            # we make the lines thinner
            # see https://github.com/matplotlib/mplfinance/blob/master/examples/widths.ipynb
            update_width_config=dict(line_width=1),
            # let's rotate the dates so that they are not angled
            xrotation=0,
            datetime_format=x_axis_datetime_format,
            ylabel="",
            ylabel_lower="",
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
        try:
            stock_info = yaticker.YaTicker.get_ticker_info(stock)
            data = yaticker.YaTicker.get_ticker_data(
                ticker=stock, period=period, interval=interval
            )
        except Exception as e:
            logging.error(f"Problem retrieving the data for {stock}... Skipping")
            logging.error(e, exc_info=True)
            return

        if not stock_info or data.empty:
            logging.error(f"Problem retrieving the data for {stock}... Skipping")
            return

        # we clear the image first
        image = util.empty_image(width=self.width, height=self.height)
        ImageDraw.Draw(image)

        # we draw the stock graph
        stock_image = Image.open(self.stock_graph(data, show_volume=self.show_volume))
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

    def display_settings(self):
        """
        Displays the currently loaded settings but also current hostname and IP address
        :return:
        """
        try:
            font_size = 10
            image = util.empty_image(width=self.width, height=self.height)
            ImageDraw.Draw(image)
            info = inspect.cleandoc(
                f"""
                Yaticker info
                -----
                hostname: {util.get_hostname()}
                IP: {util.get_ip()}
                -----
                watchlist: {self.watchlist}
                cycle: {self.cycle}
                update frequency: {self.update_frequency}
                show volume: {self.show_volume}
                period: {self.period}
            """
            )
            util.place_text(img=image, text=info, font_size=font_size)
            self.display_image(image)
        except Exception as e:
            logging.info(f"Exception: {e}")

    def cycle_through_watchlist(self):
        self.display_stock(stock=next(self._watchlist_cycle), period=self.period)
        if self.cycle is False:
            return

        s = sched.scheduler(time.time, time.sleep)

        def cycle_watchlist(sc):
            self.display_stock(stock=next(self._watchlist_cycle), period=self.period)
            s.enter(5, 1, cycle_watchlist, (sc,))

        s.enter(5, 1, cycle_watchlist, (s,))
        s.run()
