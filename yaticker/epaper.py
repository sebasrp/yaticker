import logging
import textwrap
import time

from PIL import Image, ImageOps, ImageFont, ImageDraw
from waveshare_epd import epd2in7
import RPi.GPIO as GPIO

EPD = epd2in7.EPD()
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
    display_message("Key 1 pressed")


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
        image = Image.new('1', (EPD.width, EPD.height), 255)  # 255: clear the frame
    else:
        image = Image.new('1', (EPD.height, EPD.width), 255)  # 255: clear the frame
    return image


def display_image(img):
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    epd.display_4Gray(epd.getbuffer_4Gray(img))
    epd.sleep()
    initialize_keys()
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
    try:
        image = empty_image()
        draw = ImageDraw.Draw(image)
        draw.text((95, 15), str(time.strftime("%-H:%M %p, %-d %b %Y")), fill=0)
        write_wrapped_lines(image, "Issue:" + message)
        display_image(image)
    except Exception as e:
        logging.info(f"Exception: {e}")


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
