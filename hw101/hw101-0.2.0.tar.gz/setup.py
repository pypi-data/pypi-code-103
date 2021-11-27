# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'ssd1306'}

modules = \
['MCP23017', 'MCP23S17', 'ssd1306']
install_requires = \
['smbus>=1.1.post2,<2.0', 'spidev>=3.5,<4.0']

setup_kwargs = {
    'name': 'hw101',
    'version': '0.2.0',
    'description': 'Classes for educational purposes to get started with hardware projects.',
    'long_description': '# Hardware-101 für Hardwarebausteine\n\nIn diesem Repository befinden sich für verschiedene Hardwarebausteine\ngrundlegende Informationen wie Datenblätter, Quelltext- und\nSchaltungsbeispiele sowie eine Beschreibung.\n\n![logo](img/1x/hardware-101-logo_wide.png)\n\n- [apa102](apa102): RGB-LED-Streifen mit dem Chipsatz APA102\n- [74HC595](74HC595): 8Bit-Schieberegister\n- [DS18B20](ds18b20): Temperatursensor (1-WIRE)\n- [ESP8266](esp8266): Microcontroller mit WLAN und Micropython-Unterstützung\n- [Gertboard](gertboard): Erweiterungsboard für den Raspberry Pi\n- [gpiozero](gpiozero): Einfache Bibliothek zur Ansteuerung der GPIO-Pins.\n- [HD44780](hd44780): LCD Controller\n- [led_matrix](led_matrix): Eine 5x7 LED-Matrix\n- [lm75](lm75): Temperatursensor\n- [mcp23017](mcp23017): Portexpander (I²C)\n- [mcp23s17](mcp23s17): Portexpander (SPI)\n- [mcp3208](mcp3208): Analog-Digital-Wandler (SPI)\n- [mcp3426](mcp3426): Analog-Digtial-Wandler (I²C)\n- [mcp4151](mcp4151): Digitalpotentiometer (SPI)\n- [mpu6050](mpu6050): Beschleunigungssensor und Gyrometer (I²C)\n- [Orange Pi Zero](orange_pi_zero): Einplatinencomputer\n- [RGB-LED](rgb_led): LEDs mit vielen Farben\n- [Raspberry Pi](raspi): Einplatinencomputer\n- [servo](servo): Servomotoren mittels PWM\n- [sh1106](sh1106): OLED Display Treiber\n- [ssd1306](ssd1306): OLED Display Treiber\n- [ws2811/ws2812](ws281x): RGB-LED-Streifen\n\n- [fake-rpi](fake-rpi): Hilfe für die Programmentwicklung\n- [Transistoren](Transistoren): Eine Übersicht (noch sehr übersichtlich)\n- [IO-Emulator](https://tbs1-bo.github.io/ioemu/): Emulator für Eingabe-Ausgabe-Operationen.\n\n\n## Hilf mit\n\nDu kannst das Projekt mit eigenen Beiträgen ergänzen. Schau dazu bei den  \n["good first issues"](https://github.com/tbs1-bo/hardware-101/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)\nnach, welche Themen noch benötigt werden.\n\n\n![logo](img/hardware-101-logo2.png)\n',
    'author': 'Marco Bakera',
    'author_email': 'bakera@tbs1.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hw101.tbs1.de',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
