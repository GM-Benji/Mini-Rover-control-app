import pygame
import serial
import time
from bt_receiver import print_received
import threading
from position_plot import init_plot

# Konfiguracja portu Bluetooth
BT_PORT = "COM9"
BAUDRATE = 115200

# Inicjalizacja połączenia Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=1)
    print(f"✅ Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"❌ Błąd połączenia: {e}")
    exit(1)

# Flaga wątku odbioru
running_flag = threading.Event()
running_flag.set()

# Uruchom odbiór BT w tle
receiver_thread = threading.Thread(target=print_received, args=(bt,running_flag), daemon=True)
receiver_thread.start()

# Inicjalizacja pygame i joysticka
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Brak wykrytego kontrolera Xbox! Upewnij się, że jest sparowany przez Bluetooth.")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Wykryto kontroler: {joystick.get_name()}")

# Inicjalizacja wykresu w trybie interaktywnym
init_plot(x_range=(-1000, 1000), y_range=(-1000, 1000))

# Konwersja osi joysticka na prędkość -250...250
def axis_to_speed(value, deadzone=0.15):
    if abs(value) < deadzone:
        return 0
    return int(max(min(value * 250, 250), -250))

def format_frame(left_speed, right_speed):
    if left_speed < 0 and right_speed < 0:
        sign_byte = 3
    elif left_speed < 0:
        sign_byte = 1
    elif right_speed < 0:
        sign_byte = 2
    else:
        sign_byte = 0
    l_val = abs(left_speed)
    r_val = abs(right_speed)
    frame = bytearray([l_val, r_val, sign_byte])
    return frame

# Główna pętla
try:
    while True:
        pygame.event.pump()

        axis_left_y = -joystick.get_axis(1)
        axis_right_y = -joystick.get_axis(3)

        left_speed = axis_to_speed(axis_left_y)
        right_speed = axis_to_speed(axis_right_y)

        frame = format_frame(left_speed, right_speed)

        bt.write(frame)

        time.sleep(0.02)

except KeyboardInterrupt:
    print("🛑 Zamykanie...")
finally:
    running_flag.clear()  # zatrzymaj wątek odbioru
    bt.close()
    pygame.quit()
