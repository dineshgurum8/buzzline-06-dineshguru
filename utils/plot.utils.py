import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Constants
WINDOW_SIZE = 50

# Initialize Data Storage
timestamps = deque(maxlen=WINDOW_SIZE)
vibrations = deque(maxlen=WINDOW_SIZE)
temperatures = deque(maxlen=WINDOW_SIZE)
sound_levels = deque(maxlen=WINDOW_SIZE)

def update_plot(frame, ax1, ax2, ax3):
    """Updates the live sensor plot dynamically."""
    ax1.clear()
    ax2.clear()
    ax3.clear()

    # Plot each metric
    ax1.plot(timestamps, vibrations, "b-", label="Vibration (mm/s)")
    ax2.plot(timestamps, temperatures, "r-", label="Temperature (°C)")
    ax3.plot(timestamps, sound_levels, "g-", label="Sound Level (dB)")

    # Set labels
    ax1.set_title("Vibration")
    ax2.set_title("Temperature")
    ax3.set_title("Sound Level")
    
    # Adjust layouts
    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("Time")
        ax.legend()
        ax.grid()

def setup_plot():
    """Initialize Matplotlib figure and axes."""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax1, ax2, ax3), interval=1000)
    plt.show()
