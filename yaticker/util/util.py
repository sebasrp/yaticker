import socket
import textwrap
from tempfile import NamedTemporaryFile

import requests
from matplotlib.image import imread
from PIL import Image, ImageDraw, ImageFont


def is_connected(url="http://www.google.com/", timeout=3):
    try:
        requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False


def get_ip():
    """
    Retrieve primary IP address on the local box
    see https://stackoverflow.com/a/28950776/91468
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_hostname():
    return socket.gethostname()


def number_to_string(number):
    """
    Transform a number to a string. If number is smaller than 1000, displays the last 5 significant figures.
    :param number: number to convert to string
    :return: string representation of the number
    """
    number_string = ""
    if number > 100:
        number_string = format(int(number), ",")
    else:
        number_string = str(float("%.5g" % number))
    return number_string


def get_percentage_diff(current, previous):
    if current == previous:
        return 0
    try:
        return (float(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float("inf")


# see https://kavigupta.org/2019/05/18/Setting-the-size-of-figures-in-matplotlib/
def get_size(fig, dpi=100):
    with NamedTemporaryFile(suffix=".png") as f:
        fig.savefig(f.name, bbox_inches="tight", dpi=dpi)
        height, width, _channels = imread(f.name).shape
        return width / dpi, height / dpi


def set_size(fig, size, dpi=100, eps=1e-2, give_up=2, min_size_px=10):
    target_width, target_height = size
    set_width, set_height = target_width, target_height  # reasonable starting point
    deltas = []  # how far we have
    while True:
        fig.set_size_inches([set_width, set_height])
        actual_width, actual_height = get_size(fig, dpi=dpi)
        set_width *= target_width / actual_width
        set_height *= target_height / actual_height
        deltas.append(
            abs(actual_width - target_width) + abs(actual_height - target_height)
        )
        if deltas[-1] < eps:
            return True
        if len(deltas) > give_up and sorted(deltas[-give_up:]) == deltas[-give_up:]:
            return False
        if set_width * dpi < min_size_px or set_height * dpi < min_size_px:
            return False


def empty_image(width, height):
    """
    Returns an empty canvas/image to draw  on
    :return:
    """
    return Image.new("1", (width, height), 255)  # 255: clear the frame


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
    place_text(img, text, draw_x, draw_y, font_size, font_name, fill)


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
    place_text(img, text, draw_x, draw_y, font_size, font_name, fill)


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
        place_centered_text(img, line, 0, y_text, font_size, font_name)
        y_text += height
        num_lines += 1
    return img
