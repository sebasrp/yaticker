import requests


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
