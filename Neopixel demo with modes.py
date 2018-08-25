# CircuitPython NeoPixel show with modes activated by a button.
import time
import board
import neopixel
import digitalio
import random
 
button_switch_pin = board.D2
pixel_pin = board.D5
pixel_count = 17
chase_color_duration = 3

pixels = neopixel.NeoPixel(pixel_pin, pixel_count, brightness=.1, auto_write=False)

button_state = None
mode = 0
print("Mode:", mode)

# For ItsyBitsy
button_switch = digitalio.DigitalInOut(button_switch_pin)
button_switch.direction = digitalio.Direction.INPUT
button_switch.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Colors:
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
# Sparkle colors:
GOLD = (255, 222, 30)
PINK = (242, 90, 255)
AQUA = (50, 255, 255)
JADE = (0, 255, 40)
AMBER = (255, 100, 0)
CLEAR = (0, 0, 0)
 
 
def cycle_sequence(seq):
    while True:
        yield from seq
 
 
def fade_control():
    brightness_value = iter([r / 15 for r in range(15, -1, -1)])
    while True:
        # pylint: disable=stop-iteration-return
        pixels.brightness = next(brightness_value)
        pixels.show()
        yield
 
 
def sparkle_code(color_values):
    (red_value, green_value, blue_value) = color_values
    p = random.randint(0, (pixel_count - 2))
    pixels[p] = (red_value, green_value, blue_value)
    pixels.show()
    pixels[p] = (red_value // 2, green_value // 2, blue_value // 2)
    pixels.show()
    pixels[p + 1] = (red_value // 10, green_value // 10, blue_value // 10)
    pixels.show()
    
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
 
def color_chase(color, wait):
    for i in range(pixel_count):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(pixel_count):
            rc_index = (i * 256 // pixel_count) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
#       time.sleep(wait)
 
 
fade = fade_control()
 
flash_color = cycle_sequence([RED, YELLOW, ORANGE, GREEN, TEAL, CYAN,
                              BLUE, PURPLE, MAGENTA, WHITE])
 
sparkle_color_list = (MAGENTA, PINK, GOLD, AQUA, JADE, AMBER)
sparkle_color_index = 0
 
chase_color_list = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)
 
chase_color_index = 0
chase_color_cycle = chase_color_list[chase_color_index]
offset = 0
 
chase_last_color = time.monotonic()
chase_next_color = chase_last_color + chase_color_duration
 
button_state = None
 
mode = 0
print("Mode:", mode)
 
initial_time = time.monotonic()

while True:
    try:
        now = time.monotonic()
        if not button_switch.value and button_state is None:
            button_state = "pressed"
        if button_switch.value and button_state == "pressed":
            print("Mode Change")
            led.value = True
            pixels.fill((0, 0, 0))
            mode += 1
            button_state = None
            if mode > 3: #Increase this number to add more modes.
                mode = 0
            print("Mode:,", mode)
        else:
            led.value = False
        if mode == 0:
            pixels.fill(CLEAR)
            pixels.show()
            print("Off!")
        if mode == 1:
            print("Sparkle mode activate!")
            pixels.brightness = 1
            sparkle_color_index = (sparkle_color_index + 1) \
                % len(sparkle_color_list)
            sparkle_code(sparkle_color_list[sparkle_color_index])
        if mode == 2:
            print("Chase mode activate!")
            pixels.brightness = 1
            for i in range(0, pixel_count):
                c = 0
                if ((offset + i) % 8) < 4:
                    c = chase_color_cycle
                pixels[i] = c
                pixels[(pixel_count - 1) - i] = c
            pixels.show()
            offset += 1
            if now >= chase_next_color:
                chase_color_index = (chase_color_index +
                                     1) % len(chase_color_list)
                chase_color_cycle = chase_color_list[chase_color_index]
                pixels.fill((0, 0, 0))
                chase_last_color = now
                chase_next_color = chase_last_color + chase_color_duration
        if mode == 3:
            print("Rainbow!")
            rainbow_cycle(0)
    except MemoryError:
        pass