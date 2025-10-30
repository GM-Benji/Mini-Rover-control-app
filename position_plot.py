import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue

xdata, ydata = [], []
line = None
point = None
data_queue = queue.Queue()
fig = None

def init_plot(x_range=(-1000, 1000), y_range=(-1000, 1000)):
    global line, point, fig

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

    plt.ion()            # tryb interaktywny
    plt.show(block=False)

    def update(frame):
        while not data_queue.empty():
            x, y = data_queue.get()
            xdata.append(x)
            ydata.append(y)
        if len(xdata) > 0:
            line.set_data(xdata, ydata)
            point.set_data([xdata[-1]], [ydata[-1]])
        return line, point

    ani = animation.FuncAnimation(fig, update, interval=50, blit=True, save_count=100)
