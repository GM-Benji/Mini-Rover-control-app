import pygame
import serial
import time
import struct
import matplotlib.pyplot as plt
import numpy as np

# Konfiguracja portu Bluetooth
BT_PORT = "COM9"   # zmień jeśli inny port
BAUDRATE = 115200

# Inicjalizacja połączenia Bluetooth
try:
    bt = serial.Serial(BT_PORT, BAUDRATE, timeout=0.05)
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

# Tworzenie 3-bajtowej ramki do wysyłania
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

# Inicjalizacja wykresów
plt.ion()
fig, (axA, axB) = plt.subplots(2, 1, figsize=(8, 6))

axA.set_title("Silnik A")
axA.set_xlabel("Czas [s]")
axA.set_ylabel("Prędkość")
lineA_meas, = axA.plot([], [], label="Measured Speed", color="tab:blue")
lineA_set, = axA.plot([], [], label="Set Speed", color="tab:orange")
axA.legend()
axA.grid(True)

axB.set_title("Silnik B")
axB.set_xlabel("Czas [s]")
axB.set_ylabel("Prędkość")
lineB_meas, = axB.plot([], [], label="Measured Speed", color="tab:green")
lineB_set, = axB.plot([], [], label="Set Speed", color="tab:red")
axB.legend()
axB.grid(True)

# Bufory danych
times = []
A_meas, A_set, B_meas, B_set = [], [], [], []
start_time = time.time()

# Główna pętla
try:
    while True:
        pygame.event.pump()

        # Sterowanie joystickiem
        axis_left_y = -joystick.get_axis(1)
        axis_right_y = -joystick.get_axis(3)

        left_speed = axis_to_speed(axis_left_y)
        right_speed = axis_to_speed(axis_right_y)

        frame = format_frame(left_speed, right_speed)
        bt.write(frame)

        # Próba odczytu ramki 16 bajtów
        if bt.in_waiting >= 16:
            data = bt.read(16)
            if len(data) == 16:
                # Odczytaj 4 int32 (małe endian)
                values = struct.unpack("<4i", data)
                measA, setA, measB, setB = values

                current_time = time.time() - start_time
                times.append(current_time)
                A_meas.append(measA)
                A_set.append(setA)
                B_meas.append(measB)
                B_set.append(setB)

                # Aktualizacja wykresów
                lineA_meas.set_data(times, A_meas)
                lineA_set.set_data(times, A_set)
                lineB_meas.set_data(times, B_meas)
                lineB_set.set_data(times, B_set)

                axA.relim(); axA.autoscale_view()
                axB.relim(); axB.autoscale_view()
                plt.pause(0.001)

                print(f"A: meas={measA:6d}, set={setA:6d} | B: meas={measB:6d}, set={setB:6d}")

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\n🛑 Zamykanie...")
finally:
    bt.close()
    pygame.quit()
    plt.ioff()
    plt.show()
