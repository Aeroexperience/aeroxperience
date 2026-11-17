# Squawk 777 radio tuning panel: settings you can change.
# Edit this file on the CIRCUITPY drive (hold the transfer button while plugging the panel into your Mac).

import board
from adafruit_hid.keycode import Keycode

# ---------- Wiring (ESP32-S3-DevKitC-1 pin names) ----------
# Each screen gets its own pair of pins, because both 0.91 in screens use the same address.
PIN_ACT_SDA = board.IO8      # ACTIVE screen (left)
PIN_ACT_SCL = board.IO9
PIN_SBY_SDA = board.IO1      # STANDBY screen (right)
PIN_SBY_SCL = board.IO2

PIN_KNOB_CLK = board.IO4     # tuning knob
PIN_KNOB_DT = board.IO5
PIN_KNOB_SW = board.IO6      # push the knob to switch between MHz and kHz

PIN_TFR = board.IO7          # transfer button (the arrow between the windows)
PIN_VHF_L = board.IO15
PIN_VHF_C = board.IO16
PIN_VHF_R = board.IO17

# If one click moves the frequency 2 or 4 steps, change this to 2 or 4. If it needs
# 2 clicks to move one step, change it to 1 or 2.
ENCODER_DIVISOR = 4
# If the knob counts the wrong way, set this to True.
REVERSE_KNOB = False

# Screens. 0x3C for almost every 0.91 in screen.
OLED_ADDRESS = 0x3C
# The STANDBY screen is mounted upside down (pins on the right) so its plug has room,
# so the panel turns its picture around. If a screen shows upside down, flip its value.
FLIP_ACTIVE = False
FLIP_STANDBY = True

# ---------- Frequencies the sim starts with ----------
# The Xbox can't tell the panel what the sim's radios show. The panel assumes they start
# at these values every time it powers on (active, standby). If your aircraft starts with
# something else, hold the transfer button for 3 seconds to sync (see the guide), then
# put the numbers here so you don't have to sync again.
SIM_START = {
    "L": ("118.000", "118.000"),   # VHF L = COM1
    "C": ("118.000", "118.000"),   # VHF C = COM3
    "R": ("118.000", "118.000"),   # VHF R = COM2
}

# Channel spacing in kHz. MSFS uses 25 unless the aircraft is set to 8.33 kHz mode.
STEP_KHZ = 25

# ---------- Keys sent to the Xbox ----------
# Each action presses Ctrl + Alt + Shift + one key. Bind these in MSFS:
# Settings > Controls > Keyboard, search "COM".
# (The transponder panel uses 1-4, Q, W, E, R and I, so both panels can share a profile.)
MODS = (Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT)
KEYS = {
    "L": {"WHOLE_INC": Keycode.FIVE, "WHOLE_DEC": Keycode.T,
          "FRACT_INC": Keycode.SIX, "FRACT_DEC": Keycode.Y, "SWAP": Keycode.U},
    "R": {"WHOLE_INC": Keycode.SEVEN, "WHOLE_DEC": Keycode.G,
          "FRACT_INC": Keycode.EIGHT, "FRACT_DEC": Keycode.H, "SWAP": Keycode.J},
    "C": {"WHOLE_INC": Keycode.NINE, "WHOLE_DEC": Keycode.B,
          "FRACT_INC": Keycode.ZERO, "FRACT_DEC": Keycode.N, "SWAP": Keycode.M},
}

# How long each key is held and the gap between keys, in seconds.
# If the sim misses some changes, raise both to 0.06.
KEY_HOLD = 0.035
KEY_GAP = 0.035

# ---------- Bluetooth link to Squawk ----------
BLE_NAME = "Squawk RADIO"
