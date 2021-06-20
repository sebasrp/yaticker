import logging

from yaticker.dashboard import Dashboard


class YatickerVirtual(Dashboard):

    def __init__(self):
        super().__init__(width=264, height=176, dpi=117)

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
        virtual.display_stock()
    except Exception as e:
        logging.error(e, exc_info=True)


if __name__ == "__main__":
    main()
