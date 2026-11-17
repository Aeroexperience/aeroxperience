# Runs once when the panel powers on.
# Normal start: the panel shows up ONLY as a USB keyboard, which is what the Xbox wants.
# Edit mode: hold the transfer button while plugging in, and the CIRCUITPY drive shows up on your Mac.

import board
import digitalio
import storage
import usb_cdc
import usb_hid

try:
    import usb_midi
    usb_midi.disable()
except ImportError:
    pass

tfr = digitalio.DigitalInOut(board.IO7)   # transfer button
tfr.switch_to_input(pull=digitalio.Pull.UP)
edit_mode = not tfr.value   # button pulls the pin low when pressed
tfr.deinit()

usb_hid.enable((usb_hid.Device.KEYBOARD,), boot_device=1)

if not edit_mode:
    storage.disable_usb_drive()
    usb_cdc.disable()

try:
    import supervisor
    supervisor.disable_ble_workflow()   # keep Bluetooth free for the Squawk link
except Exception:
    pass
