import logging
import textwrap
import time
from datetime import datetime

import currency
import mplfinance as mplf
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from util import util
from waveshare_epd import epd2in7

from yaticker import yaticker

EPD = epd2in7.EPD()
eHEIGHT = EPD.height
eWIDTH = EPD.width
eDPI = 117

# PIN numbers of the physical buttons
KEY_1 = 5
KEY_2 = 6
KEY_3 = 13
KEY_4 = 19


def initialize_keys():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(KEY_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def btn_1_press():
    display_stock()


def btn_2_press():
    display_message("Key 2 pressed")


def btn_3_press():
    display_message("Key 3 pressed")


def btn_4_press():
    display_message("Key 4 pressed")


def empty_image(orientation="horizontal"):
    """
    Returns an empty canvas/image to draw  on
    :return:
    """
    if orientation == "vertical":
        image = Image.new("1", (eWIDTH, eHEIGHT), 255)  # 255: clear the frame
    else:
        image = Image.new("1", (eHEIGHT, eWIDTH), 255)  # 255: clear the frame
    return image


def display_image(img):
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    epd.display_4Gray(epd.getbuffer_4Gray(img))
    epd.sleep()
    initialize_keys()
    return


def _place_text(
    img, text, x_offset=0, y_offset=0, font_size=40, font_name="Forum-Regular", fill=0
):
    """
    Put some text at a location on the image.
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
    draw.text((x_offset, y_offset), text, font=font, fill=fill)


def _place_centered_text(
    img, text, x_offset=0, y_offset=0, font_size=40, font_name="Forum-Regular", fill=0
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
    _place_text(img, text, draw_x, draw_y, font_size, font_name, fill)


def _place_text_right(
    img, text, x_offset=0, y_offset=0, font_size=40, font_name="Forum-Regular", fill=0
):
    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    draw_x = (img_width - text_width) + x_offset
    draw_y = y_offset
    _place_text(img, text, draw_x, draw_y, font_size, font_name, fill)


def _stock_graph(data, height=116, width=264, filename="candle.png"):
    fig, _ = mplf.plot(
        data,
        type="line",
        figsize=(width / eDPI, height / eDPI),
        axisoff=True,
        tight_layout=True,
        scale_padding=0.2,
        returnfig=True,
    )
    fig.savefig(filename, dpi=eDPI)
    return filename


def write_wrapped_lines(
    img, text, font_size=16, y_text=20, height=15, width=25, font_name="Roboto-Light"
):
    lines = textwrap.wrap(text, width)
    num_lines = 0
    for line in lines:
        _place_centered_text(img, line, 0, y_text, font_size, font_name)
        y_text += height
        num_lines += 1
    return img


def display_message(message):
    try:
        image = empty_image()
        draw = ImageDraw.Draw(image)
        draw.text((95, 15), str(time.strftime("%-H:%M %p, %-d %b %Y")), fill=0)
        write_wrapped_lines(image, message)
        display_image(image)
    except Exception as e:
        logging.info(f"Exception: {e}")


def display_stock(stock="amzn", period: str = "1440m", interval: str = "5m"):
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
    image = empty_image()
    ImageDraw.Draw(image)

    # we draw the stock graph
    stock_image = Image.open(_stock_graph(data))
    image.paste(stock_image, (0, 0))

    # we draw the latest stock's price
    latest_price = data["Close"][-1]
    closing_str = f"{currency.symbol('USD')}{util.number_to_string(latest_price)}"
    stock_price_font_size = 48
    y_offset = ((eWIDTH - stock_price_font_size) / 2) - 12
    x_offset = -29
    _place_centered_text(
        img=image,
        text=closing_str,
        font_size=stock_price_font_size,
        x_offset=x_offset,
        y_offset=y_offset,
        font_name="Roboto-Medium",
    )

    # we put the stock name at the bottom right of the graph
    symbol_font_size = 20
    y_offset = eWIDTH - stock_price_font_size
    _place_text_right(
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
        y_offset = eWIDTH - stock_price_font_size + symbol_font_size
        _place_text_right(
            img=image,
            text=diff_str,
            font_size=diff_font_size,
            y_offset=y_offset,
            font_name="Roboto-Medium",
        )

    # date of last ticker data at the bottom
    last_data_time = data.index[-1].tz_convert('Asia/Singapore').strftime("%-H:%M %p, %-d %b %Y")

    last_date_font_size = 10
    y_offset = (eWIDTH - last_date_font_size) / 2
    _place_centered_text(
        img=image,
        text=last_data_time,
        font_size=last_date_font_size,
        y_offset=y_offset,
        font_name="Roboto-Medium",
    )

    # we display the final image
    display_image(image)


def full_screen_update():
    try:
        display_message("Welcome to Yaticker")
    except Exception as e:
        logging.info(f"Exception: {e}")
    return time.time()


def display_info():
    full_screen_update()


def needs_refresh():
    return False


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        display_info()
        initialize_keys()
        while True:
            key_1_state = GPIO.input(KEY_1)
            key_2_state = GPIO.input(KEY_2)
            key_3_state = GPIO.input(KEY_3)
            key_4_state = GPIO.input(KEY_4)

            if not key_1_state:
                btn_1_press()
                time.sleep(0.2)
            if not key_2_state:
                btn_2_press()
                time.sleep(0.2)
            if not key_3_state:
                btn_3_press()
                time.sleep(0.2)
            if not key_4_state:
                btn_4_press()
                time.sleep(0.2)
    except Exception as e:
        logging.error(e, exc_info=True)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        GPIO.cleanup()
        exit()


if __name__ == "__main__":
    main()
