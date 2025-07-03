import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window


class PhysicsBody(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    position = ReferenceListProperty(position_x, position_y)


class ThreeBodySim(Widget):
    body1 = ObjectProperty(None)
    body2 = ObjectProperty(None)
    body3 = ObjectProperty(None)

    def initialize_sim(self):
        self.body1 = PhysicsBody(pos=(Window.width/2 + 100, Window.height/2), size=(10, 10))
        self.body2 = PhysicsBody(pos=(Window.width/2 + 0, Window.height/2), size=(10, 10))
        self.body3 = PhysicsBody(pos=(Window.width/2 - 100, Window.height/2), size=(10, 10))
        self.add_widget(self.body1)
        self.add_widget(self.body2)
        self.add_widget(self.body3)
        pass

    def update(self, dt):
        pass


class ThreeBodyProblem(App):
    def build(self):
        sim = ThreeBodySim()
        sim.initialize_sim()
        Clock.schedule_interval(sim.update, 1.0 / 60.0)
        return sim


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
        # gravitation_force is added to the new force here because if there is more than two bodies in the simulation
        # then we need to add the totals up. But at the end of update_velocity_and_position we reset the total
        # gravitational_force to zero to recalculate gravity based on the new positions
        self.gravitational_force = self.gravitational_force + -G * ((exterting_body.mass * self.mass) * (self.position - exterting_body.position)) \
                                   / (np.linalg.norm(self.position - exterting_body.position) ** 3)

    def update_velocity_and_position(self, delta_time):
        # Convert Force vector applied by gravity to velocity
        self.velocity = self.velocity + ((self.gravitational_force / self.mass) * delta_time)

        # Convert velocity into position
        self.position = self.position + (self.velocity * delta_time)

        # Reset the gravitational_force since positions have changed, thus changing the gravitational effects
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

    history3_x = body3.position_history_x[:step]
    history3_y = body3.position_history_y[:step]

    # Plot positions
    trace_body1.set_data(history1_x, history1_y)
    trace_body2.set_data(history2_x, history2_y)
    trace_body3.set_data(history3_x, history3_y)

    time_text.set_text(time_template % step)

    return trace_body1, trace_body2, trace_body3, time_text


if __name__ == '__main__':
    ThreeBodyProblem().run()
else:
    body1 = Body(2, np.array([0, 1]), np.array([-1, 0]))
    body2 = Body(2, np.array([0, -1]), np.array([1, 0]))
    body3 = Body(2, np.array([0, 0]), np.array([0, 0]))

    frame_time = float(input("What is the frame time: "))
    time_scale = int(input("Number of frames to calculate through: "))

    for i in range(time_scale):
        # Print the progress of the calculations
        if (i % 100) == 0:
            print("{}%".format(round((i / time_scale) * 100), 2))

        body1.calc_gravitational_force(body2)
        body1.calc_gravitational_force(body3)
        body2.calc_gravitational_force(body1)
        body2.calc_gravitational_force(body3)
        body3.calc_gravitational_force(body1)
        body3.calc_gravitational_force(body2)

        body1.update_velocity_and_position(frame_time)
        body2.update_velocity_and_position(frame_time)
        body3.update_velocity_and_position(frame_time)

    x_min, x_max = find_min_max_between_arrays(body1.position_history_x, body2.position_history_x)
    y_min, y_max = find_min_max_between_arrays(body1.position_history_y, body2.position_history_y)

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(autoscale_on=False, xlim=(x_min-1, x_max+1), ylim=(y_min-1, y_max+1))

    time_template = 'Frame = %d'
    time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

    # Create the trace line that is a point followed by a solid line
    trace_body1, = ax.plot([], [], '.-', lw=1, ms=2)
    trace_body2, = ax.plot([], [], '.-', lw=1, ms=2)
    trace_body3, = ax.plot([], [], '.-', lw=1, ms=2)

    ani = animation.FuncAnimation(fig, animate, time_scale, interval=10, blit=True)
    ax.grid(True)
    plt.show()
