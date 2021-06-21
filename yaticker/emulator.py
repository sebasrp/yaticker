import logging

from yaticker.dashboard import Dashboard


class YatickerVirtual(Dashboard):
    """This emulates the size of the epaper 2in7, but displays the output to the console"""

    def __init__(
        self, width=264, height=176, dpi=117, config_file="yaticker/config.yaml"
    ):
        super().__init__(width=width, height=height, dpi=dpi, config_file=config_file)

    def display_image(self, img):
        try:
            img.show()
        except Exception as e:
            logging.info(f"Exception: {e}")
        return


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        virtual = YatickerVirtual()
        virtual.display_settings()
    except Exception as e:
        logging.error(e, exc_info=True)


if __name__ == "__main__":
    main()
