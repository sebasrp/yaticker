import logging
import textwrap
import time
from abc import ABC, abstractmethod

import currency
import mplfinance as mplf
from PIL import Image, ImageDraw, ImageFont
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

    def empty_image(self, orientation="horizontal"):
        """
        Returns an empty canvas/image to draw  on
        :return:
        """
        if orientation == "vertical":
            image = Image.new(
                "1", (self.width, self.height), 255
            )  # 255: clear the frame
        else:
            image = Image.new(
                "1", (self.height, self.width), 255
            )  # 255: clear the frame
        return image

    @staticmethod
    def place_text(
        img,
        text,
        x_offset=0,
        y_offset=0,
        font_size=40,
        font_name="Forum-Regular",
        fill=0,
    ):
        """
        Put some text at a location on the image.
        """
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
        draw.text((x_offset, y_offset), text, font=font, fill=fill)

    @staticmethod
    def place_centered_text(
        img,
        text,
        x_offset=0,
        y_offset=0,
        font_size=40,
        font_name="Forum-Regular",
        fill=0,
    ):
        """
        Put some centered text at a location on the image.
        """
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
        img_width, img_height = img.size
        text_width, _ = font.getsize(text)
        text_height = font_size
        draw_x = (img_width - text_width) // 2 + x_offset
        draw_y = (img_height - text_height) // 2 + y_offset
        Dashboard.place_text(img, text, draw_x, draw_y, font_size, font_name, fill)

    @staticmethod
    def place_text_right(
        img,
        text,
        x_offset=0,
        y_offset=0,
        font_size=40,
        font_name="Forum-Regular",
        fill=0,
    ):
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
        img_width, img_height = img.size
        text_width, _ = font.getsize(text)
        draw_x = (img_width - text_width) + x_offset
        draw_y = y_offset
        Dashboard.place_text(img, text, draw_x, draw_y, font_size, font_name, fill)

    @staticmethod
    def write_wrapped_lines(
        img,
        text,
        font_size=16,
        y_text=20,
        height=15,
        width=25,
        font_name="Roboto-Light",
    ):
        lines = textwrap.wrap(text, width)
        num_lines = 0
        for line in lines:
            Dashboard.place_centered_text(img, line, 0, y_text, font_size, font_name)
            y_text += height
            num_lines += 1
        return img

    def display_message(self, message):
        try:
            image = self.empty_image()
            draw = ImageDraw.Draw(image)
            draw.text((95, 15), str(time.strftime("%-H:%M %p, %-d %b %Y")), fill=0)
            Dashboard.write_wrapped_lines(image, message)
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
        image = self.empty_image()
        ImageDraw.Draw(image)

        # we draw the stock graph
        stock_image = Image.open(self.stock_graph(data))
        image.paste(stock_image, (0, 0))

        # we draw the latest stock's price
        latest_price = data["Close"][-1]
        closing_str = f"{currency.symbol('USD')}{util.number_to_string(latest_price)}"
        stock_price_font_size = 48
        y_offset = ((self.width - stock_price_font_size) / 2) - 12
        x_offset = -29
        Dashboard.place_centered_text(
            img=image,
            text=closing_str,
            font_size=stock_price_font_size,
            x_offset=x_offset,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

        # we put the stock name at the bottom right of the graph
        symbol_font_size = 20
        y_offset = self.width - stock_price_font_size
        Dashboard.place_text_right(
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
            y_offset = self.width - stock_price_font_size + symbol_font_size
            Dashboard.place_text_right(
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
        y_offset = (self.width - last_date_font_size) / 2
        Dashboard.place_centered_text(
            img=image,
            text=last_data_time,
            font_size=last_date_font_size,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

        # we display the final image
        self.display_image(image)
