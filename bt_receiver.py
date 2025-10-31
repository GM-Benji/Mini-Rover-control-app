import time
from position_plot import add_point
import struct

def print_received(bt_serial, running_flag):
    """
    Wątek odbioru danych z robota:
    Robot wysyła 4 int32 = 16 bajtów (little-endian)
    Pierwsze 2 int32 to X i Y.
    """
    while running_flag.is_set():
        try:
            if bt_serial.in_waiting >= 16:
                raw = bt_serial.read(16)
                x, y, _, _ = struct.unpack('<iiii', raw)
                add_point(x, y)
                print(f"Odebrane: X={x}  Y={y}")
            else:
                time.sleep(0.01)
        except Exception as e:
            print("Błąd odbioru:", e)
            time.sleep(0.05)
