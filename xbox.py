import pygame
import serial
import time
import threading
from bt_receiver import print_received
from position_plot import start_plot, clear_plot

# ==============================
# 🔧 KONFIGURACJA BLUETOOTH
# ==============================
BT_PORT = "COM9"
BAUDRATE = 115200

try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=1)
    print(f"✅ Połączono z HC-06 na {BT_PORT}")
except serial.SerialException as e:
    print(f"❌ Błąd połączenia: {e}")
    exit(1)

# Flaga działania dla wątku odbiornika
running_flag = threading.Event()
running_flag.set()

# ==============================
# 🛰️ ODBIÓR DANYCH W TLE
# ==============================
receiver_thread = threading.Thread(target=print_received, args=(bt, running_flag), daemon=True)
receiver_thread.start()

# ==============================
# 🎮 INICJALIZACJA KONTROLERA
# ==============================
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Brak wykrytego kontrolera Xbox!")
    exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Wykryto kontroler: {joystick.get_name()}")

# ==============================
# 📈 URUCHOMIENIE WYKRESU
# ==============================
start_plot(x_range=(-1000, 1000), y_range=(-1000, 1000))

# ==============================
# 🧮 FUNKCJE POMOCNICZE
# ==============================
def axis_to_speed(value, deadzone=0.15):
    """Konwersja osi joysticka (-1...1) na prędkość -250...250"""
    if abs(value) < deadzone:
        return 0
    return int(max(min(value * 250, 250), -250))

def format_frame(left_speed, right_speed):
    """Tworzy ramkę sterującą dla robota"""
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
    return bytearray([l_val, r_val, sign_byte])

# ==============================
# 🔁 GŁÓWNA PĘTLA
# ==============================
try:
    while True:
        pygame.event.pump()

        # Odczyt osi Y z lewej i prawej gałki
        axis_left_y = -joystick.get_axis(1)
        axis_right_y = -joystick.get_axis(3)

        left_speed = axis_to_speed(axis_left_y)
        right_speed = axis_to_speed(axis_right_y)

        # Wysyłanie ramki sterującej do robota
        frame = format_frame(left_speed, right_speed)
        bt.write(frame)

        # 🔵 Przycisk X (index 2) – czyszczenie wykresu (jednorazowe kliknięcie)
        if joystick.get_button(2) and not hasattr(clear_plot, "_pressed"):
            print("🧹 Czyszczenie wykresu...")
            clear_plot()
            clear_plot._pressed = True
        elif not joystick.get_button(2):
            if hasattr(clear_plot, "_pressed"):
                delattr(clear_plot, "_pressed")

        time.sleep(0.02)

except KeyboardInterrupt:
    print("🛑 Zamykanie...")

finally:
    running_flag.clear()
    bt.close()
    pygame.quit()
