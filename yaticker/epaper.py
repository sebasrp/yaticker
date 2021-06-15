import logging
import textwrap
import time

from PIL import Image, ImageOps, ImageFont, ImageDraw
import RPi.GPIO as GPIO
from waveshare_epd import epd2in7

EPD = epd2in7.EPD()


def empty_image(orientation="horizontal"):
    """
    Returns an empty canvas/image to draw  on
    :return:
    """
    if orientation == "vertical":
        image = Image.new('1', (EPD.width, EPD.height), 255)  # 255: clear the frame
    else:
        image = Image.new('1', (EPD.height, EPD.width), 255)  # 255: clear the frame
    return image


def display_image(img):
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    epd.display_4Gray(epd.getbuffer_4Gray(img))
    epd.sleep()
    return


def _place_text(img, text, x_offset=0, y_offset=0, font_size=40, font_name="Forum-Regular", fill=0):
    """
    Put some centered text at a location on the image.
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', font_size)
    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = font_size
    draw_x = (img_width - text_width) // 2 + x_offset
    draw_y = (img_height - text_height) // 2 + y_offset
    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def write_wrapped_lines(img, text, font_size=16, y_text=20, height=15, width=25, font_name="Roboto-Light"):
    lines = textwrap.wrap(text, width)
    num_lines = 0
    for line in lines:
        _place_text(img, line, 0, y_text, font_size, font_name)
        y_text += height
        num_lines += 1
    return img


def display_message(message):
    image = empty_image()
    draw = ImageDraw.Draw(image)
    draw.text((95, 15), str(time.strftime("%-H:%M %p, %-d %b %Y")), fill=0)
    write_wrapped_lines(image, "Issue:" + message)
    return image


def full_screen_update():
    try:
        image = display_message("Hello World")
        display_image(image)
    except Exception as e:
        logging.info(f"Exception: {e}")
    return time.time()


def display_info():
    full_screen_update()


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        display_info()
    except Exception as e:
        logging.info(f"Exception: {e}")
        epd2in7.epdconfig.module_exit()
        GPIO.cleanup()
        exit()


if __name__ == "__main__":
    main()
