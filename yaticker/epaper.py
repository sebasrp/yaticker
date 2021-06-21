import logging
import time

import RPi.GPIO as GPIO
from waveshare_epd import epd2in7

from yaticker.dashboard import Dashboard


class EPaper2in7(Dashboard):
    EPD = epd2in7.EPD()

    # PIN numbers of the physical buttons
    KEY_1 = 5
    KEY_2 = 6
    KEY_3 = 13
    KEY_4 = 19

    def __init__(
        self,
        width=EPD.height,
        height=EPD.width,
        dpi=117,
        config_file="yaticker/config.yaml",
    ):
        # EPD default orientation is vertical, we swap the default height / width
        super().__init__(width=width, height=height, dpi=dpi, config_file=config_file)
        self.initialize_keys()

    def initialize_keys(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.KEY_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def btn_1_press(self):
        self.cycle_through_watchlist()

    def btn_2_press(self):
        self.display_message("Key 2 pressed")

    def btn_3_press(self):
        self.display_message("Key 3 pressed")

    def btn_4_press(self):
        self.display_settings()

    def display_image(self, img):
        try:
            epd = epd2in7.EPD()
            epd.Init_4Gray()
            epd.display_4Gray(epd.getbuffer_4Gray(img))
            epd.sleep()
            self.initialize_keys()
        except Exception as e:
            logging.info(f"Exception: {e}")
        return

    def run(self):
        try:
            while True:
                key_1_state = GPIO.input(self.KEY_1)
                key_2_state = GPIO.input(self.KEY_2)
                key_3_state = GPIO.input(self.KEY_3)
                key_4_state = GPIO.input(self.KEY_4)

                if not key_1_state:
                    self.btn_1_press()
                    time.sleep(0.2)
                if not key_2_state:
                    self.btn_2_press()
                    time.sleep(0.2)
                if not key_3_state:
                    self.btn_3_press()
                    time.sleep(0.2)
                if not key_4_state:
                    self.btn_4_press()
                    time.sleep(0.2)
        except Exception as e:
            logging.error(e, exc_info=True)
        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd2in7.epdconfig.module_exit()
            GPIO.cleanup()
            exit()


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        epaper = EPaper2in7()
        epaper.display_message("Welcome to Yaticker")
        epaper.run()
    except Exception as e:
        logging.error(e, exc_info=True)


if __name__ == "__main__":
    main()
