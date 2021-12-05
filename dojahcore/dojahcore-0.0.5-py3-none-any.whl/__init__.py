""" Script contains all the constants used in the application """

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv(
    'DOJAH_API_KEY',
    'test_sk_qgTTdKFhWJjguEerqwP5MKOQw'
)
APP_ID = os.getenv(
    'DOJAH_APP_ID',
    '619bc460c423930034a34052'
)

API_URL = 'https://api.dojah.io' if API_KEY[0:4] != 'test' else 'https://sandbox.dojah.io'