# Squawk 777 transponder panel: settings you can change.
# Edit this file on the CIRCUITPY drive (hold IDENT while plugging the panel into your Mac).

import board
from adafruit_hid.keycode import Keycode

# ---------- Wiring (ESP32-S3-DevKitC-1 pin names) ----------
PIN_SDA = board.IO8          # OLED SDA
PIN_SCL = board.IO9          # OLED SCL

PIN_LEFT_CLK = board.IO4     # left code knob (first two digits)
PIN_LEFT_DT = board.IO5
PIN_LEFT_SW = board.IO6      # push the left knob to switch between digit 1 and 2

PIN_RIGHT_CLK = board.IO15   # right code knob (last two digits)
PIN_RIGHT_DT = board.IO16
PIN_RIGHT_SW = board.IO17    # push the right knob to switch between digit 3 and 4

PIN_MODE_CLK = board.IO10    # mode selector knob
PIN_MODE_DT = board.IO11

PIN_IDENT = board.IO13       # IDENT button (hold while plugging in = edit mode)

# If a knob moves 2 or 4 numbers per click, change this to 2 or 4. If it needs
# 2 clicks to move one number, change it to 1 or 2.
ENCODER_DIVISOR = 4

# The mode knob needs this many clicks per position (labels on the faceplate are 2 clicks apart).
MODE_CLICKS = 2

# If a knob counts the wrong way, set its value to True.
REVERSE_LEFT = False
REVERSE_RIGHT = False
REVERSE_MODE = False

# OLED address. Almost always 0x3C. Some boards use 0x3D.
OLED_ADDRESS = 0x3C

# ---------- Code the sim starts with ----------
# The Xbox can't tell the panel what code the sim has. The panel assumes the sim
# starts at this code each time it powers on. Most aircraft start at 1200 in the US.
# If the sim shows something else, hold IDENT for 3 seconds to sync (see the guide).
SIM_START_CODE = "1200"

# ---------- Keys sent to the Xbox ----------
# Each action presses Ctrl + Alt + Shift + one key. Bind these in MSFS:
# Settings > Controls > Keyboard, search "transponder".
MODS = (Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT)
KEYS = {
    "1000_INC": Keycode.ONE,
    "1000_DEC": Keycode.Q,
    "100_INC": Keycode.TWO,
    "100_DEC": Keycode.W,
    "10_INC": Keycode.THREE,
    "10_DEC": Keycode.E,
    "1_INC": Keycode.FOUR,
    "1_DEC": Keycode.R,
    "IDENT": Keycode.I,
}

# How long each key is held and the gap between keys, in seconds.
# If the sim misses some changes, raise both to 0.06.
KEY_HOLD = 0.035
KEY_GAP = 0.035

# ---------- Bluetooth link to Squawk ----------
BLE_NAME = "Squawk XPDR"
