import pygame
import serial
import time

# Konfiguracja portu Bluetooth (zmień na właściwy port dla HC-06)
BT_PORT = "/dev/rfcomm1"  # Musisz wcześniej sparować HC-06 i przypisać port szeregowy
BAUDRATE = 115200

# Inicjalizacja Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=1)
    print(f"Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"Błąd połączenia: {e}")
    exit(1)

# Inicjalizacja pygame dla joysticka
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Brak wykrytego joysticka!")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Wykryto joystick: {joystick.get_name()}")

def get_percentage(value, deadzone=0.15):
    """
    Przekształca wartość z zakresu -1.0 do 1.0 na 0–99 z martwą strefą.
    Wszystko pomiędzy -deadzone a +deadzone traktowane jako 0.
    """
    if abs(value) < deadzone:
        return 0
    return int(min(max(abs(value) * 99, 0), 99))

def get_direction(value, axis_type, last_dir):
    if axis_type == "forward":
        if value < -0.2:
            return "F"
        elif value > 0.2:
            return "B"
        else:
            return last_dir
    if axis_type == "turn":
        if value < -0.2:
            return "L"
        elif value > 0.2:
            return "R"
        else:
            return last_dir

def format_frame(fb, fb_val, lr, lr_val):
    return f"{fb}{fb_val:02}{lr}{lr_val:02}"

last_fb_dir = "F"
last_lr_dir = "L"

try:
    while True:
        pygame.event.pump()  # aktualizuje dane z joysticka

        axis_y = joystick.get_axis(1)  # Oś przód/tył
        axis_x = joystick.get_axis(0)  # Oś lewo/prawo

        fb_pct = get_percentage(axis_y, deadzone=0.15)
        fb_dir = get_direction(axis_y, "forward", last_fb_dir)
        if fb_pct != 0:
            last_fb_dir = fb_dir

        lr_pct = get_percentage(axis_x, deadzone=0.30)
        lr_dir = get_direction(axis_x, "turn", last_lr_dir)
        if lr_pct != 0:
            last_lr_dir = lr_dir

        frame = format_frame(fb_dir, fb_pct, lr_dir, lr_pct)
        print(f"Wysyłanie: {frame}")
        bt.write(frame.encode('ascii'))

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Zamykanie...")
finally:
    bt.close()
    pygame.quit()