import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue
import time

# ==============================
# GLOBALNE ZMIENNE
# ==============================
xdata, ydata = [], []
data_queue = queue.Queue()

# Obiekty Matplotlib
fig = None
ax = None
line = None
point = None
ani = None

# Flaga działania wątku
plot_running = True


# ==============================
# 🔹 Funkcja dodająca nowy punkt
# ==============================
def add_point(x, y):
    """Dodaje nowy punkt (x, y) do kolejki."""
    data_queue.put((x, y))


# ==============================
# 🔹 Czyszczenie wykresu
# ==============================
def clear_plot():
    """Czyści trajektorię robota na wykresie."""
    global xdata, ydata
    xdata.clear()
    ydata.clear()
    print("🧹 Wykres wyczyszczony")


# ==============================
# 🔹 Aktualizacja wykresu
# ==============================
def update(frame):
    """Aktualizuje dane na wykresie co kilka ms."""
    global xdata, ydata

    # Odbierz wszystkie nowe punkty z kolejki
    while not data_queue.empty():
        x, y = data_queue.get()
        xdata.append(x)
        ydata.append(y)

    if len(xdata) > 0:
        line.set_data(xdata, ydata)
        point.set_data([xdata[-1]], [ydata[-1]])

    return line, point


# ==============================
# 🔹 Wątek z animacją
# ==============================
def plot_thread(x_range=(-1000, 1000), y_range=(-1000, 1000)):
    """Uruchamia animację Matplotlib w głównym wątku GUI."""
    global fig, ax, line, point, ani, plot_running

    plt.ion()  # tryb interaktywny (umożliwia współpracę z innymi wątkami)
    fig, ax = plt.subplots()
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_title("Pozycja robota w czasie rzeczywistym")

    line, = ax.plot([], [], 'b-', linewidth=2, label='trajektoria')
    point, = ax.plot([], [], 'ro', label='aktualna pozycja')
    ax.legend()

    # uruchom animację
    ani = animation.FuncAnimation(fig, update, interval=50, blit=True, cache_frame_data=False)

    print("📈 Wykres uruchomiony.")
    plt.show(block=True)

    plot_running = False
    print("📉 Wykres zamknięty.")


# ==============================
# 🔹 Start wykresu w osobnym wątku
# ==============================
def start_plot(x_range=(-1000, 1000), y_range=(-1000, 1000)):
    """Uruchamia wątek z animacją (bez blokowania programu głównego)."""
    thread = threading.Thread(target=plot_thread, args=(x_range, y_range), daemon=True)
    thread.start()
    time.sleep(0.5)  # chwila na inicjalizację
