import pygame
import serial
import time

# Konfiguracja portu Bluetooth
BT_PORT = "COM9"
BAUDRATE = 115200

# Inicjalizacja Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=1)
    print(f"Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"Błąd połączenia: {e}")
    exit(1)

# Inicjalizacja pygame
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Brak wykrytego joysticka!")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Wykryto joystick: {joystick.get_name()}")

# Konwersja osi joysticka na prędkości -250…250
def axis_to_speed(value, deadzone=0.15):
    if abs(value) < deadzone:
        return 0
    return int(max(min(value * 250, 250), -250))

# Funkcja do tworzenia ramki 8-bajtowej
def format_frame(left_speed, right_speed):
    # wyznacz znaki prędkości
    left_sign = '0' if left_speed >= 0 else '1'
    right_sign = '0' if right_speed >= 0 else '1'

    # wartości bezwzględne
    l_val = abs(left_speed)
    r_val = abs(right_speed)

    # 3 cyfry każda (zero-padding, np. 007)
    l_str = f"{l_val:03}"
    r_str = f"{r_val:03}"

    # złożenie w ramkę 8 bajtów
    return (l_str + r_str + left_sign + right_sign).encode('ascii')

try:
    while True:
        pygame.event.pump()

        axis_y = joystick.get_axis(1)  # przód/tył
        axis_x = joystick.get_axis(0)  # lewo/prawo

        # różnicowe sterowanie: lewa/prawa prędkość
        base_speed = axis_to_speed(-axis_y, deadzone=0.15)   # oś Y = prędkość bazowa
        turn = axis_to_speed(axis_x, deadzone=0.15)          # oś X = skręt

        left_speed = base_speed - turn
        right_speed = base_speed + turn

        # przycięcie do zakresu -250…250
        left_speed = max(min(left_speed, 250), -250)
        right_speed = max(min(right_speed, 250), -250)

        # utworzenie ramki
        frame = format_frame(left_speed, right_speed)

        print(f"L: {left_speed:4}  R: {right_speed:4}  -> {frame}")
        bt.write(frame)

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Zamykanie...")
finally:
    bt.close()
    pygame.quit()
