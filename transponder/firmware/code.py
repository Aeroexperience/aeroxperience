# Squawk 777 transponder panel
# - Plugs into the Xbox as a USB keyboard and sends transponder key presses to MSFS.
# - Talks to the Squawk web app over Bluetooth so ATC can check your code.
#
# Controls (like the 777 ATC panel):
#   Left knob:  turn = change the selected digit (1 or 2), push = switch digit 1 <-> 2
#   Right knob: turn = change the selected digit (3 or 4), push = switch digit 3 <-> 4
#   Mode knob:  STBY, ALT OFF, XPNDR, TA ONLY, TA/RA
#   IDENT:      press = ident. Hold 3 s = SYNC (tell the panel what the sim shows).

import time
import board
import busio
import displayio
import keypad
import rotaryio
import terminalio
import usb_hid
import vectorio

from adafruit_display_text import label
from adafruit_hid.keyboard import Keyboard
import adafruit_displayio_ssd1306

import settings as C

try:
    import i2cdisplaybus
    def make_bus(i2c):
        return i2cdisplaybus.I2CDisplayBus(i2c, device_address=C.OLED_ADDRESS)
except ImportError:   # CircuitPython 8
    def make_bus(i2c):
        return displayio.I2CDisplay(i2c, device_address=C.OLED_ADDRESS)

MODES = ("STBY", "ALT OFF", "XPNDR", "TA ONLY", "TA/RA")
PLACE = ("1000", "100", "10", "1")

# ---------------- state ----------------
# Both start at the sim's starting code. (The Xbox may still be on the menu when the
# panel powers on, so the panel never sends keys until you turn a knob.)
sim = [int(c) for c in C.SIM_START_CODE]          # what we think the sim shows
panel = list(sim)                                 # what the panel shows
mode = 4                                          # TA/RA
mode_acc = mode * C.MODE_CLICKS
sel_left, sel_right = 0, 2                        # selected digit for each knob
ident_until = 0
sync_mode = False
assigned = ""                                     # code ATC gave you (from Squawk)
queue = []                                        # key actions waiting to be sent

def plan_keys(i, diff):
    """Queue key presses to move digit i of the sim by diff steps."""
    name = PLACE[i] + ("_INC" if diff > 0 else "_DEC")
    for _ in range(abs(diff)):
        queue.append(name)
        sim[i] = (sim[i] + (1 if diff > 0 else -1)) % 8


# ---------------- hardware ----------------
kbd = None
try:
    kbd = Keyboard(usb_hid.devices)
except Exception as e:
    print("No USB keyboard (not plugged into a host?)", e)

def enc(a, b):
    return rotaryio.IncrementalEncoder(a, b, divisor=C.ENCODER_DIVISOR)

e_left = enc(C.PIN_LEFT_CLK, C.PIN_LEFT_DT)
e_right = enc(C.PIN_RIGHT_CLK, C.PIN_RIGHT_DT)
e_mode = enc(C.PIN_MODE_CLK, C.PIN_MODE_DT)
last = [e_left.position, e_right.position, e_mode.position]

buttons = keypad.Keys((C.PIN_LEFT_SW, C.PIN_RIGHT_SW, C.PIN_IDENT), value_when_pressed=False, pull=True)
B_LEFT, B_RIGHT, B_IDENT = 0, 1, 2
ident_down_at = None

# ---------------- display ----------------
displayio.release_displays()
i2c = busio.I2C(C.PIN_SCL, C.PIN_SDA, frequency=400000)
display = adafruit_displayio_ssd1306.SSD1306(make_bus(i2c), width=128, height=64)
root = displayio.Group()
display.root_group = root

white = displayio.Palette(1)
white[0] = 0xFFFFFF

top_left = label.Label(terminalio.FONT, text="", x=0, y=5)
top_right = label.Label(terminalio.FONT, text="", x=104, y=5)
code_lbl = label.Label(terminalio.FONT, text="1200", scale=3, x=28, y=28)
bottom = label.Label(terminalio.FONT, text="", x=0, y=58)
underline = vectorio.Rectangle(pixel_shader=white, width=16, height=2, x=28, y=48)
for item in (top_left, top_right, code_lbl, underline, bottom):
    root.append(item)

DIGIT_W = 18   # terminalio glyph is 6 px wide, scale 3

def draw():
    code_lbl.text = "".join(str(d) for d in panel)
    # underline the two digits the knob you last touched controls
    first = sel_left if active_side == "L" else sel_right
    underline.x = code_lbl.x + first * DIGIT_W
    underline.width = DIGIT_W - 2
    if sync_mode:
        top_left.text = "SYNC: set sim code"
        bottom.text = "IDENT = done"
    else:
        top_left.text = ("ATC " + assigned) if assigned else ""
        bottom.text = ("IDENT  " if time.monotonic() < ident_until else "") + MODES[mode]
    top_right.text = "BT" if ble_connected() else ""

active_side = "L"

# ---------------- Bluetooth (Squawk link) ----------------
ble = uart = None
try:
    from adafruit_ble import BLERadio
    from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
    from adafruit_ble.services.nordic import UARTService
    ble = BLERadio()
    ble.name = C.BLE_NAME
    uart = UARTService()
    adv = ProvideServicesAdvertisement(uart)
    adv.complete_name = C.BLE_NAME
except Exception as e:
    print("Bluetooth not available:", e)

def ble_connected():
    try:
        return bool(ble and ble.connected)
    except Exception:
        return False

def ble_send():
    if not ble_connected():
        return
    msg = "C%s M%d I%d\n" % ("".join(str(d) for d in panel), mode, 1 if time.monotonic() < ident_until else 0)
    try:
        uart.write(msg.encode())
    except Exception:
        pass

def ble_poll():
    global assigned
    if not ble:
        return
    try:
        if not ble.connected and not ble.advertising:
            ble.start_advertising(adv)
        if ble.connected and uart.in_waiting:
            line = uart.readline()
            if line:
                s = line.decode().strip()
                if s.startswith("A") and len(s) >= 5 and s[1:5].isdigit():
                    assigned = s[1:5]
                elif s == "A":
                    assigned = ""
                elif s == "?":
                    ble_send()
    except Exception as e:
        print("BLE:", e)

# ---------------- key sending ----------------
next_key_at = 0

def pump_keys(now):
    global next_key_at
    if not queue or now < next_key_at:
        return
    action = queue.pop(0)
    if kbd:
        try:
            kbd.press(*C.MODS, C.KEYS[action])
            time.sleep(C.KEY_HOLD)
            kbd.release_all()
        except Exception as e:
            print("USB:", e)
    next_key_at = time.monotonic() + C.KEY_GAP

# ---------------- main loop ----------------
def change_digit(i, steps):
    panel[i] = (panel[i] + steps) % 8
    if sync_mode:
        sim[i] = panel[i]           # just telling the panel what the sim shows
    else:
        plan_keys(i, steps)

last_ble = 0
draw()
while True:
    now = time.monotonic()
    changed = False

    # knobs
    pos = [e_left.position, e_right.position, e_mode.position]
    d = [pos[k] - last[k] for k in range(3)]
    last = pos
    if C.REVERSE_LEFT: d[0] = -d[0]
    if C.REVERSE_RIGHT: d[1] = -d[1]
    if C.REVERSE_MODE: d[2] = -d[2]
    if d[0]:
        active_side = "L"; change_digit(sel_left, d[0]); changed = True
    if d[1]:
        active_side = "R"; change_digit(sel_right, d[1]); changed = True
    if d[2]:
        mode_acc = max(0, min((len(MODES) - 1) * C.MODE_CLICKS, mode_acc + d[2]))
        mode = mode_acc // C.MODE_CLICKS; changed = True

    # buttons
    ev = buttons.events.get()
    while ev:
        if ev.key_number == B_LEFT and ev.pressed:
            sel_left = 1 if sel_left == 0 else 0; active_side = "L"; changed = True
        elif ev.key_number == B_RIGHT and ev.pressed:
            sel_right = 3 if sel_right == 2 else 2; active_side = "R"; changed = True
        elif ev.key_number == B_IDENT:
            if ev.pressed:
                ident_down_at = now
            elif ident_down_at is not None:
                held = now - ident_down_at
                ident_down_at = None
                if sync_mode:
                    sync_mode = False            # done syncing; panel and sim now match
                elif held >= 3:
                    sync_mode = True             # long press: start syncing
                else:
                    queue.append("IDENT")
                    ident_until = now + 18       # the sim turns ident off after 18 s
                changed = True
        ev = buttons.events.get()
    if ident_down_at is not None and not sync_mode and now - ident_down_at >= 3:
        sync_mode = True; ident_down_at = None; changed = True

    pump_keys(now)
    ble_poll()

    if changed:
        draw()
        ble_send()
        last_ble = now
    elif now - last_ble > 1:
        draw()        # keeps the IDENT and BT indicators current
        ble_send()
        last_ble = now
    time.sleep(0.005)
