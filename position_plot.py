import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue

# Globalne
xdata, ydata = [], []
line = None
point = None
data_queue = queue.Queue()

def init_plot(x_range=(-10, 10), y_range=(-10, 10)):
    """
    Tworzy i uruchamia wykres, który sam się aktualizuje,
    gdy do kolejki dodane są nowe punkty.
    """
    global line, point

    fig, ax = plt.subplots()
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_title("Pozycja robota w czasie rzeczywistym")
    ax.grid(True)

    line, = ax.plot([], [], 'b-', linewidth=2, label='trajektoria')
    point, = ax.plot([], [], 'ro', label='aktualna pozycja')
    ax.legend()

    # funkcja aktualizacji wywoływana co 50 ms przez główny wątek
    def update(frame):
        while not data_queue.empty():
            x, y = data_queue.get()
            xdata.append(x)
            ydata.append(y)

        if len(xdata) > 0:
            line.set_data(xdata, ydata)
            point.set_data([xdata[-1]], [ydata[-1]])  # <-- poprawka tutaj
        return line, point


    ani = animation.FuncAnimation(fig, update, interval=50, blit=True)
    plt.show()


def add_point(x, y):
    """
    Wywołuj z innego wątku (np. z odbioru BT),
    żeby przekazać nowe dane do wykresu.
    """
    data_queue.put((x, y))
