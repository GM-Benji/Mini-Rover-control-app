import pygame
import serial
import time
import sys
import glob

# === AUTOMATYCZNE WYKRYWANIE URZĄDZENIA BLUETOOTH ===
def find_bt_port():
    # Szukaj potencjalnych portów BT
    possible_ports = glob.glob("/dev/rfcomm*") + glob.glob("/dev/tty.*") + glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyAMA*")

    if not possible_ports:
        print("❌ Nie znaleziono żadnych portów szeregowych Bluetooth (rfcomm, ttyUSB, ttyAMA, tty.*).")
        print("🔹 Upewnij się, że HC-06 jest sparowany i połączony, np.:")
        print("   sudo rfcomm bind /dev/rfcomm0 XX:XX:XX:XX:XX:XX")
        sys.exit(1)

    print("🔍 Wykryte porty:", possible_ports)

    for port in possible_ports:
        try:
            bt = serial.Serial(port, 115200, timeout=1)
            time.sleep(0.5)
            if bt.is_open:
                print(f"✅ Połączono z HC-06 (lub innym BT) na {port}")
                return bt
        except serial.SerialException:
            continue

    print("❌ Nie udało się otworzyć żadnego portu Bluetooth.")
    sys.exit(1)

# === INICJALIZACJA POŁĄCZENIA ===
bt = find_bt_port()

# === INICJALIZACJA PYGAME I KONTROLERA ===
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Brak wykrytego kontrolera Xbox! Upewnij się, że jest sparowany przez Bluetooth lub podłączony kablem USB.")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Wykryto kontroler: {joystick.get_name()}")

# === FUNKCJE POMOCNICZE ===
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
    return bytearray([l_val, r_val, sign_byte])

# === GŁÓWNA PĘTLA ===
try:
    while True:
        pygame.event.pump()

        # Xbox Controller: lewa gałka Y = oś 1, prawa Y = oś 4
        axis_left_y = -joystick.get_axis(1)
        axis_right_y = -joystick.get_axis(3)

        left_speed = axis_to_speed(axis_left_y_
