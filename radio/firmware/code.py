# Squawk 777 radio tuning panel (replica of the Boeing 777 RTP)
# - Plugs into the Xbox as a USB keyboard and sends COM radio key presses to MSFS.
# - Talks to the Squawk web app over Bluetooth, so Squawk tunes to whatever the panel shows.
#
# Controls:
#   VHF L / VHF C / VHF R: pick which radio the panel tunes (COM1 / COM3 / COM2)
#   Tuning knob: turn = change the STANDBY frequency, push = switch between MHz and kHz
#   Transfer button (arrow): swap ACTIVE and STANDBY. Hold 3 s = SYNC (tell the panel what the sim shows).

import time
import board
import busio
import keypad
import rotaryio
import usb_hid

import adafruit_ssd1306
from adafruit_hid.keyboard import Keyboard

import settings as C

RADIO_NAMES = ("L", "C", "R")
STEP = C.STEP_KHZ

def parse(f):
    mhz, _, khz = f.partition(".")
    return int(mhz) * 1000 + int((khz + "000")[:3])

def fmt(k):
    return "%03d%03d" % (k // 1000, k % 1000)

# ---------------- state ----------------
# What the panel shows. It always matches the sim, except while syncing.
radios = {r: [parse(C.SIM_START[r][0]), parse(C.SIM_START[r][1])] for r in RADIO_NAMES}
sel = "L"               # radio being tuned
fine = True             # True = knob changes kHz, False = MHz
focus_until = 0         # underline the part the knob changes, for a few seconds after you touch it
sync_mode = False
hint = 0                # frequency ATC asked for (from Squawk), shown briefly on STANDBY
hint_until = 0
queue = []              # key actions waiting to be sent: (radio, action)

def step_standby(clicks):
    """Move the standby frequency of the selected radio, like MSFS does (no carry between MHz and kHz)."""
    k = radios[sel][1]
    mhz, khz = k // 1000, k % 1000
    for _ in range(abs(clicks)):
        up = clicks > 0
        if fine:
            if up:
                khz = (khz // STEP + 1) * STEP % 1000
            else:
                khz = ((khz + STEP - 1) // STEP - 1) * STEP % 1000
        else:
            mhz += 1 if up else -1
            if mhz > 136: mhz = 118
            if mhz < 118: mhz = 136
        if not sync_mode:
            queue.append((sel, ("FRACT_" if fine else "WHOLE_") + ("INC" if up else "DEC")))
    radios[sel][1] = mhz * 1000 + khz

def transfer():
    a, s = radios[sel]
    radios[sel] = [s, a]
    if not sync_mode:
        queue.append((sel, "SWAP"))

# ---------------- hardware ----------------
kbd = None
try:
    kbd = Keyboard(usb_hid.devices)
except Exception as e:
    print("No USB keyboard (not plugged into a host?)", e)

knob = rotaryio.IncrementalEncoder(C.PIN_KNOB_CLK, C.PIN_KNOB_DT, divisor=C.ENCODER_DIVISOR)
last_pos = knob.position

buttons = keypad.Keys((C.PIN_KNOB_SW, C.PIN_TFR, C.PIN_VHF_L, C.PIN_VHF_C, C.PIN_VHF_R),
                      value_when_pressed=False, pull=True)
B_KNOB, B_TFR, B_L, B_C, B_R = range(5)
tfr_down_at = None

# ---------------- displays ----------------
# Two 0.91 in 128x32 screens, each on its own I2C pins.
def make_screen(sda, scl, flip):
    try:
        i2c = busio.I2C(scl, sda, frequency=400000)
        d = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=C.OLED_ADDRESS)
        if flip:
            d.rotate(False)
        return d
    except Exception as e:
        print("Screen not found on", sda, scl, e)
        return None

scr_act = make_screen(C.PIN_ACT_SDA, C.PIN_ACT_SCL, C.FLIP_ACTIVE)
scr_sby = make_screen(C.PIN_SBY_SDA, C.PIN_SBY_SCL, C.FLIP_STANDBY)

# Segment digits like the 777 LCD: "118.300" filling the right side of each screen.
DW, DH, T, GAP, DOT = 14, 28, 3, 4, 5
X0 = 128 - (6 * DW + 5 * GAP + DOT) - 1
Y0 = 1
SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd",
        6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcdfg"}

def digit_x(i):
    return X0 + i * (DW + GAP) + (DOT if i >= 3 else 0)

def seg_digit(d, x, y, n):
    h2 = DH // 2
    box = {
        "a": (x + T, y, DW - 2 * T, T),
        "b": (x + DW - T, y + T, T, h2 - T),
        "c": (x + DW - T, y + h2, T, h2 - T),
        "d": (x + T, y + DH - T, DW - 2 * T, T),
        "e": (x, y + h2, T, h2 - T),
        "f": (x, y + T, T, h2 - T),
        "g": (x + T, y + h2 - T // 2, DW - 2 * T, T),
    }
    for s in SEGS[n]:
        d.fill_rect(*box[s], 1)

def draw_freq(d, k):
    s = fmt(k)
    for i, ch in enumerate(s):
        seg_digit(d, digit_x(i), Y0, int(ch))
    dx = digit_x(2) + DW + (GAP + DOT) // 2 - 2
    d.fill_rect(dx, Y0 + DH - 3, 3, 3, 1)

# Tiny 5x7 letters for the labels on the left edge.
FONT = {
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F), "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11), "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04), "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11), "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
}

def letter(d, x, y, ch, scale=1):
    rows = FONT.get(ch)
    if not rows:
        return
    for r, bits in enumerate(rows):
        for c in range(5):
            if bits & (0x10 >> c):
                d.fill_rect(x + c * scale, y + r * scale, scale, scale, 1)

def vertical(d, word):
    for i, ch in enumerate(word):
        letter(d, 4, 1 + i * 10, ch)

_last = None

def draw():
    global _last
    now = time.monotonic()
    act, sby = radios[sel]
    show_hint = hint and now < hint_until and not sync_mode
    focus = (0 if not fine else 1) if (now < focus_until or sync_mode) else -1
    bt = ble_connected()
    blink = sync_mode and int(now * 2) % 2
    state = (sel, act, sby, show_hint, hint, focus, bt, sync_mode, blink)
    if state == _last:
        return
    _last = state
    if scr_act:
        scr_act.fill(0)
        letter(scr_act, 2, 4, sel, 2)                  # which radio: L, C or R
        if bt:
            scr_act.fill_rect(2, 27, 3, 3, 1)         # small dot = Squawk connected
        draw_freq(scr_act, act)
        scr_act.show()
    if scr_sby:
        scr_sby.fill(0)
        if show_hint:
            vertical(scr_sby, "ATC")
            draw_freq(scr_sby, hint)
        else:
            if sync_mode:
                if blink:
                    vertical(scr_sby, "SYN")
            draw_freq(scr_sby, sby)
            if focus >= 0:
                x1 = digit_x(3 * focus)
                scr_sby.fill_rect(x1, 30, digit_x(3 * focus + 2) + DW - x1, 2, 1)
        scr_sby.show()

# ---------------- Bluetooth (Squawk link) ----------------
ble = uart = adv = None
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
    parts = ["V" + sel]
    for r in RADIO_NAMES:
        parts.append("%s%s,%s" % (r, fmt(radios[r][0]), fmt(radios[r][1])))
    parts.append("S%d" % (1 if sync_mode else 0))
    try:
        uart.write((" ".join(parts) + "\n").encode())
    except Exception:
        pass

def ble_poll():
    global hint, hint_until
    if not ble:
        return
    try:
        if not ble.connected and not ble.advertising:
            ble.start_advertising(adv)
        if ble.connected and uart.in_waiting:
            line = uart.readline()
            if line:
                s = line.decode().strip()
                if s.startswith("H") and len(s) == 7 and s[1:].isdigit():
                    k = int(s[1:4]) * 1000 + int(s[4:7])
                    if k != hint:
                        hint, hint_until = k, time.monotonic() + 5   # ATC's new frequency
                elif s == "H":
                    hint = 0
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
    radio, action = queue.pop(0)
    if kbd:
        try:
            kbd.press(*C.MODS, C.KEYS[radio][action])
            time.sleep(C.KEY_HOLD)
            kbd.release_all()
        except Exception as e:
            print("USB:", e)
    next_key_at = time.monotonic() + C.KEY_GAP

# ---------------- main loop ----------------
last_ble = 0
last_draw = 0
draw()
while True:
    now = time.monotonic()
    changed = False

    pos = knob.position
    d = pos - last_pos
    last_pos = pos
    if C.REVERSE_KNOB:
        d = -d
    if d:
        step_standby(d)
        hint_until = 0
        focus_until = now + 3
        changed = True

    ev = buttons.events.get()
    while ev:
        k = ev.key_number
        if k == B_KNOB and ev.pressed:
            fine = not fine; focus_until = now + 3; hint_until = 0; changed = True
        elif k in (B_L, B_C, B_R) and ev.pressed:
            sel = RADIO_NAMES[k - B_L]; hint_until = 0; changed = True
        elif k == B_TFR:
            if ev.pressed:
                tfr_down_at = now
            elif tfr_down_at is not None:
                held = now - tfr_down_at
                tfr_down_at = None
                if held < 3:
                    transfer()
                    hint_until = 0
                    changed = True
        ev = buttons.events.get()
    if tfr_down_at is not None and now - tfr_down_at >= 3:
        sync_mode = not sync_mode          # hold 3 s to start syncing, and again to finish
        tfr_down_at = None
        focus_until = now + 3
        changed = True

    pump_keys(now)
    ble_poll()

    if changed:
        draw()
        ble_send()
        last_ble = now
    else:
        if now - last_draw > 0.25:
            draw()    # only redraws when something on screen changed (timers, BT, blinking)
            last_draw = now
        if now - last_ble > 1:
            ble_send()
            last_ble = now
    time.sleep(0.005)
