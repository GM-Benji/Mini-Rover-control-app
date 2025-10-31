import matplotlib.pyplot as plt
import threading
import queue
import time

# Kolejka punktów (thread-safe)
data_queue = queue.Queue()
xdata, ydata = [], []

def add_point(x, y):
    """Dodaje punkt do kolejki wykresu"""
    data_queue.put((x, y))

def start_plot(x_range=(-1000, 1000), y_range=(-1000, 1000)):
    """
    Uruchamia wątek, który rysuje wykres w czasie rzeczywistym.
    Nie blokuje głównej pętli (pygame).
    """
    def plot_loop():
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([], [], 'b-', linewidth=2, label='trajektoria')
        point, = ax.plot([], [], 'ro', label='aktualna pozycja')
        ax.set_xlim(*x_range)
        ax.set_ylim(*y_range)
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_title("Pozycja robota w czasie rzeczywistym")
        ax.grid(True)
        ax.legend()

        while True:
            updated = False
            while not data_queue.empty():
                x, y = data_queue.get()
                xdata.append(x)
                ydata.append(y)
                updated = True

            if updated and xdata:
                line.set_data(xdata, ydata)
                point.set_data([xdata[-1]], [ydata[-1]])
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()

            time.sleep(0.05)  # odświeżanie co 50 ms

    t = threading.Thread(target=plot_loop, daemon=True)
    t.start()
