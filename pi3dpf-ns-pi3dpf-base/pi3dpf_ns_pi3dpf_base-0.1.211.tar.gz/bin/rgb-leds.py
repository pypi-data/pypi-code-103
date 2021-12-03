#!/usr/bin/env python3
# From: https://pypi.org/project/rpi-ws281x/ [and http://static.kancloud.cn/xpro/gpiozero/1513923]
#
# NeoPixel library strand test example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strand test example.  Showcases
# various animations on a strip of NeoPixels.

import time, os, configparser, argparse
from rpi_ws281x import PixelStrip, Color, ws
from pi3dpf_ns.pi3dpf_common import pf_common as pfc
from pi3dpf_ns.pi3dpf_base import pf as aaa # only needed to determine config file location

this_dir = os.path.dirname(__file__)
this_file = os.path.basename(__file__)
config_file = [os.path.join(os.path.dirname(aaa.__file__), 'cfg', 'pf.config')]
cfg = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                                converters={'list': lambda x: [i.strip() for i in x.split(',')]})
if os.path.isfile('/home/pi/.pf/pf.config'):
    config_file.append('/home/pi/.pf/pf.config')
cfg.cfg_fname = config_file
cfg.read(config_file)
LOG_DIR = pfc.get_config_param(cfg, 'LOG_DIR')
print("LOG_DIR={}".format(LOG_DIR))

# LED strip configuration:
LED_COUNT = pfc.get_config_param(cfg, 'LED_COUNT')  # Number of LED pixels.
LED_PIN = pfc.get_config_param(cfg, 'LED_PIN')  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN      = pfc.get_config_param(cfg, 'LED_PIN')         # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = pfc.get_config_param(cfg, 'LED_FREQ_HZ')  # LED signal frequency in hertz (usually 800khz)
LED_DMA = pfc.get_config_param(cfg, 'LED_DMA')  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = pfc.get_config_param(cfg, 'LED_BRIGHTNESS')  # Set to 0 for darkest and 255 for brightest
LED_INVERT = pfc.get_config_param(cfg,
                                  'LED_INVERT')  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = pfc.get_config_param(cfg, 'LED_CHANNEL')  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP_TXT = pfc.get_config_param(cfg, 'LED_STRIP')
LED_STRIP = eval(LED_STRIP_TXT)  # eval needed to convert strings like ws.SK6812_STRIP_RGBW to its int value
LED_RGB_ORDER = pfc.get_config_param(cfg, 'LED_RGB_ORDER')  # some strips expect color in GBR or other order. BRG, RGB


class ColCode:

    def __init__(self, coding='RGB'):
        self.coding = coding
        self.def_color
        # RBG
        self.red = self.def_color((255, 0, 0))
        self.aqua = self.def_color((0, 255, 255))
        self.blue = self.def_color((0, 0, 255))
        self.green = self.def_color((0, 255, 0))
        self.yellow = self.def_color((255, 255, 0))
        self.fuchsia = self.def_color((255, 0, 255))
        self.white = self.def_color((255, 255, 255))
        self.maroon = self.def_color((128, 0, 0))
        self.black = self.def_color((0, 0, 0))
        self.orange = self.def_color((255, 165, 0))
        self.compWhite = self.def_color((255, 255, 255, 255))

    def def_color(self, rgb_colorcode):
        c = [-1, -1, -1]
        for i, b in enumerate(('R', 'G', 'B')):
            idx = self.coding.find(b)
            if idx < 0 or idx > 2:
                print("implementation error")
                exit(1)
            #     import pdb; pdb.set_trace()
            c[idx] = rgb_colorcode[i]
        print(c)
        return (Color(red=c[0], green=c[1], blue=c[2]))


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wakeupLight(strip, color, duration_s=30, direction='sunrise'):
    step = 1 if direction == 'sunrise' else -1
    dimLight(strip, color, duration_s, step)


def dimLight(strip, color, duration_s=30, increment=1):
    #  colorWipe(strip, col.black, 10)
    strip.setBrightness(0)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    elapsedTime = 0
    step = duration_s / 255
    brightness = 0 if increment > 0 else 255
    threshold = 255 if increment > 0 else 0
    # import pdb; pdb.set_trace()
    while brightness <= 255 and brightness >= 0:
        # print("brightness: {}".format(brightness))
        strip.setBrightness(brightness)
        strip.show()
        time.sleep(step)
        brightness += increment


def sunRise(strip, color, duration_s=30):
    #  colorWipe(strip, col.black, 10)
    strip.setBrightness(0)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    elapsedTime = 0
    step = duration_s / 255
    brightness = 0
    while brightness < 255:
        # print("brightness: {}".format(brightness))
        strip.setBrightness(brightness)
        strip.show()
        time.sleep(step)
        brightness += 1


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument("-a", "--animation-mode", default="demo",
                        choices=["demo", "color-wipe", "theater-chase", "rainbow", "sunrise", "sunset"],
                        help="type of animation to start")
    parser.add_argument("-n", "--named-color", default="blue",
                        choices=["red", "aqua", "blue", "green", "yellow", "fuchsia", "white", "maroon", "black",
                                 "orange", "compWhite"], help="Color to use")
    parser.add_argument("-o", "--rgb-order", default=LED_RGB_ORDER, choices=["RGB", "GRB", "BRG", "RBG", "GBR", "BGR"],
                        help="order in which to pass the colors")
    parser.add_argument("-d", "--duration", default=30, action='store',
                        help="duration in seconds --animation=sunrise is going to last")

    args = parser.parse_args()

    col = ColCode(coding=args.rgb_order)
    sunrise_duration = int(args.duration)
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        led_color = {
            "red": col.red,
            "aqua": col.aqua,
            "blue": col.blue,
            "green": col.green,
            "yellow": col.yellow,
            "fuchsia": col.fuchsia,
            "white": col.white,
            "maroon": col.maroon,
            "black": col.black,
            "orange": col.orange,
            "compWhite": col.compWhite
        }[args.named_color]
    except KeyError:
        led_color = col.blue

    #  print('0x{:06X}'.format(65280))
    print('     LED strip type: {}'.format(LED_STRIP_TXT))
    print('     selected color: -n {}'.format(args.named_color))
    print('    RGB color order: {}'.format(args.rgb_order))
    print('selected color code: 0x{:06X}'.format(led_color))
    try:

        while True:
            if args.animation_mode in ['demo', 'color-wipe']:
                print('Color wipe animations.')
                colorWipe(strip, col.red)  # Red wipe
                colorWipe(strip, col.blue)  # Blue wipe
                colorWipe(strip, col.green)  # Green wipe
            if args.animation_mode in ['demo', 'theater-chase']:
                print('Theater chase animations.')
                theaterChase(strip, Color(127, 127, 127))  # White theater chase
                theaterChase(strip, Color(127, 0, 0))  # Red theater chase
                theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            if args.animation_mode in ['demo', 'rainbow']:
                print('Rainbow animations.')
                rainbow(strip)
                rainbowCycle(strip)
                theaterChaseRainbow(strip)
            if args.animation_mode in ['sunrise', 'sunset']:
                print('Sunrise animations.')
                print(args.named_color)
                # sunRise(strip, led_color, sunrise_duration)
                wakeupLight(strip, led_color, sunrise_duration, args.animation_mode)
                if args.animation_mode in ['sunrise', 'sunset']:
                    if args.clear:
                        colorWipe(strip, col.black, 10)
                    exit(0)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, col.black, 10)
