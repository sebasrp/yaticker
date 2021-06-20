from tempfile import NamedTemporaryFile

import requests
from matplotlib.image import imread


def is_connected(url="http://www.google.com/", timeout=3):
    try:
        requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False


def number_to_string(number):
    """
    Transform a number to a string. If number is smaller than 1000, displays the last 5 significant figures.
    :param number: number to convert to string
    :return: string representation of the number
    """
    number_string = ""
    if number > 1000:
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
