import struct
import serial
import time
from position_plot import data_queue
def receive_frame(bt_serial):
    # Odczytaj 16 bajtów
    data = bt_serial.read(16)
    if len(data) != 16:
        return None  # Niepełna ramka

    # Rozpakuj 4 int32 little-endian
    ints = struct.unpack('<4i', data)
    return ints

def add_point(x, y):
    data_queue.put((x, y))


def print_received(bt_serial, running_flag):
    while running_flag.is_set():
        try:
            data = bt_serial.read(16)
            if len(data) == 16:
                frame = struct.unpack('<4i', data)
                add_point(frame[0], frame[1])
                print(f"Odebrane wartości: {frame}")
            else:
                # Poczekaj chwilę lub obsłuż niepełną ramkę
                time.sleep(0.01)
        except serial.SerialException:
            print("Port zamknięty lub błąd odczytu.")
            break

