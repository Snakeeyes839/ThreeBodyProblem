import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Body:
    """Establishes a physical body"""

    def __init__(self, mass, initial_pos, initial_v):
        self.mass = mass
        self.position = initial_pos
        self.velocity = initial_v
        self.gravitational_force = np.array([0.0, 0.0])
        self.position_history_x = [np.array(initial_pos[0])]
        self.position_history_y = [np.array(initial_pos[1])]

    def calc_gravitational_force(self, exterting_body):
        G = 1
        # G = 6.6743e−11

        # Newton's Law of Universal Gravitation in Vector Form
        # Fg = -G * (m1m2 / |r_21|^3) * r_21
        self.gravitational_force = self.gravitational_force + -G * ((exterting_body.mass * self.mass) * (self.position - exterting_body.position)) \
                                   / (np.linalg.norm(self.position - exterting_body.position) ** 3)

    def update_velocity_and_position(self, delta_time):
        # Convert Force vector applied by gravity to velocity
        self.velocity = self.velocity + ((self.gravitational_force / self.mass) * delta_time)

        # Convert velocity into position
        self.position = self.position + (self.velocity * delta_time)
        self.gravitational_force = [0, 0]

        # Record the history for the plot animation
        self.position_history_x.append(self.position[0])
        self.position_history_y.append(self.position[1])


def find_min_max_between_arrays(arr1, arr2):
    if min(arr1) < min(arr2):
        minimum = min(arr1)
    else:
        minimum = min(arr2)

    if max(arr1) > max(arr2):
        maximum = max(arr1)
    else:
        maximum = max(arr2)

    return minimum, maximum


# animate a plot with the gravitational data calculated
def animate(step):
    history1_x = body1.position_history_x[:step]
    history1_y = body1.position_history_y[:step]
    history2_x = body2.position_history_x[:step]
    history2_y = body2.position_history_y[:step]

    # Plot positions
    trace_body1.set_data(history1_x, history1_y)
    trace_body2.set_data(history2_x, history2_y)
    time_text.set_text(time_template % step)
    return trace_body1, trace_body2, time_text


body1 = Body(2, np.array([0, .5]), np.array([-1, 0]))
body2 = Body(2, np.array([0, -.5]), np.array([1, 0]))

frame_time = float(input("What is the frame time: "))
time_scale = int(input("Number of frames to calculate through: "))

for i in range(time_scale):
    # Print the progress of the calculations
    if (i % 100) == 0:
        print("{}%".format(round((i / time_scale) * 100), 2))

    body1.calc_gravitational_force(body2)
    body2.calc_gravitational_force(body1)

    body1.update_velocity_and_position(frame_time)
    body2.update_velocity_and_position(frame_time)

x_min, x_max = find_min_max_between_arrays(body1.position_history_x, body2.position_history_x)
y_min, y_max = find_min_max_between_arrays(body1.position_history_y, body2.position_history_y)

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(autoscale_on=False, xlim=(x_min-1, x_max+1), ylim=(y_min-1, y_max+1))

time_template = 'Frame = %d'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

# Create the trace line that is a point followed by a solid line
trace_body1, = ax.plot([], [], '.-', lw=1, ms=2)
trace_body2, = ax.plot([], [], '.-', lw=1, ms=2)

ani = animation.FuncAnimation(fig, animate, time_scale, interval=10, blit=True)
ax.grid(True)
plt.show()
