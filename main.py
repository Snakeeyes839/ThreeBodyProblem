import numpy as np
import matplotlib.pyplot as plt


class Body:
    """Establishes a physical body"""

    def __init__(self, mass, initial_pos, initial_v):
        self.mass = mass
        self.position = initial_pos
        self.velocity = initial_v
        self.gravitational_force = np.array([0.0, 0.0])

    def calc_gravitational_force(self, exterting_body):
        G = 1
        # G = .066743

        # Newton's Law of Universal Gravitation in Vector Form
        # Fg = -G * (m1m2 / |r_21|^3) * r_21
        self.gravitational_force = -G * ((exterting_body.mass * self.mass) * (self.position - exterting_body.position)) \
                                   / (np.linalg.norm(self.position - exterting_body.position) ** 3)

    def update_velocity_and_position(self, delta_time):
        # Convert Force vector applied by gravity to velocity
        self.velocity = self.velocity + ((self.gravitational_force / self.mass) * delta_time)

        # Convert velocity into position
        self.position = self.position + (self.velocity * delta_time)


body1 = Body(2, np.array([0.0, 1]), np.array([-1, .01]))
body2 = Body(2, np.array([0.0, 0]), np.array([1, -.01]))

frame_time = float(input("What is the frame time: "))
time_scale = int(input("Number of frames to calculate through: "))

fig, ax = plt.subplots()

for i in range(time_scale):
    # Print the progress of the calculations
    if (i % 100) == 0:
        print("{}%".format((i / time_scale) * 100))

    body1.calc_gravitational_force(body2)
    body2.calc_gravitational_force(body1)

    body1.update_velocity_and_position(frame_time)
    body2.update_velocity_and_position(frame_time)

    # Plot positions
    ax.scatter(body1.position[0], body1.position[1], c='red', s=10)
    ax.scatter(body2.position[0], body2.position[1], c='blue', s=10)

ax.grid(True)
plt.show()