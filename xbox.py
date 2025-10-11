import pygame
import serial
import time

# Konfiguracja portu Bluetooth
BT_PORT = "COM9"   # zmień jeśli inny port
BAUDRATE = 115200

# Inicjalizacja połączenia Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=1)
    print(f"✅ Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"❌ Błąd połączenia: {e}")
    exit(1)

# Inicjalizacja pygame i joysticka
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Brak wykrytego kontrolera Xbox! Upewnij się, że jest sparowany przez Bluetooth.")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Wykryto kontroler: {joystick.get_name()}")

# Konwersja osi joysticka na prędkość -250...250
def axis_to_speed(value, deadzone=0.15):
    if abs(value) < deadzone:
        return 0
    return int(max(min(value * 250, 250), -250))

# Tworzenie ramki 8-bajtowej
def format_frame(left_speed, right_speed):
    left_sign = '0' if left_speed >= 0 else '1'
    right_sign = '0' if right_speed >= 0 else '1'

    l_val = abs(left_speed)
    r_val = abs(right_speed)

    l_str = f"{l_val:03}"
    r_str = f"{r_val:03}"

    return (l_str + r_str + left_sign + right_sign).encode('ascii')

# Główna pętla
try:
    while True:
        pygame.event.pump()

        # Uwaga: w kontrolerach Xbox:
        # oś 1 = lewa gałka Y (odwrócona: -1 = przód, 1 = tył)
        # oś 4 = prawa gałka Y (odwrócona: -1 = przód, 1 = tył)
        axis_left_y = -joystick.get_axis(1)   # lewa prędkość
        axis_right_y = -joystick.get_axis(3)  # prawa prędkość

        left_speed = axis_to_speed(axis_left_y)
        right_speed = axis_to_speed(axis_right_y)

        frame = format_frame(left_speed, right_speed)
        print(f"L: {left_speed:4}  R: {right_speed:4}  -> {frame.decode()}")
        bt.write(frame)

        time.sleep(0.02)

except KeyboardInterrupt:
    print("🛑 Zamykanie...")
finally:
    bt.close()
    pygame.quit()
