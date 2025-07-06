from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window


class PhysicsBody(Widget):
    mass = NumericProperty(10)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    gravitational_force_x = NumericProperty(0)
    gravitational_force_y = NumericProperty(0)
    gravitational_force = ReferenceListProperty(gravitational_force_x, gravitational_force_y)

    def set_initial_conditions(self, mass, init_v):
        self.mass = mass
        self.velocity = init_v

    def calc_gravitational_force(self, exerting_body):
        # G = 6.6743e−11
        G = 1

        # Newton's Law of Universal Gravitation in Vector Form
        # Fg = -G * (m1m2 / |r_21|^3) * r_21
        # gravitation_force is added to the new force here because if there is more than two bodies in the simulation
        # then we need to add the totals up. But at the end of update_velocity_and_position we reset the total
        # gravitational_force to zero to recalculate gravity based on the new positions
        m1m2 = self.mass * exerting_body.mass
        b1b2_displacement = Vector(self.center) - Vector(exerting_body.center)
        b1b2_magnitude = b1b2_displacement.length()

        self.gravitational_force = (-G * (m1m2 * b1b2_displacement) / (b1b2_magnitude ** 3)) + self.gravitational_force

    def update_velocity_and_position(self, delta_time):
        # Convert Force vector applied by gravity to velocity
        self.velocity = ((Vector(*self.gravitational_force) / self.mass) * delta_time) + self.velocity

        # Convert velocity into position
        self.center = (Vector(*self.velocity) * delta_time) + self.center

        # Reset the gravitational_force since positions have changed, thus changing the gravitational effects
        self.gravitational_force = [0, 0]


class ThreeBodySim(Widget):
    body1 = ObjectProperty(None)
    body2 = ObjectProperty(None)
    body3 = ObjectProperty(None)

    def initialize_sim(self):
        window_h_center = Window.height / 2
        window_w_center = Window.width / 2

        r1 = 5
        r2 = 40
        r3 = 5

        self.body1 = PhysicsBody(pos=(window_w_center + 100 - r1, window_h_center - r1), size=(2*r1, 2*r1))
        self.body2 = PhysicsBody(pos=(window_w_center - r2, window_h_center - r2), size=(2*r2, 2*r2))
        self.body3 = PhysicsBody(pos=(window_w_center - 100 - r3, window_h_center - r3), size=(2*r3, 2*r3))

        self.body1.set_initial_conditions(200, Vector(0, -30))
        self.body2.set_initial_conditions(100000, Vector(0, 0))
        self.body3.set_initial_conditions(200, Vector(0, 30))

        self.add_widget(self.body1)
        self.add_widget(self.body2)
        self.add_widget(self.body3)

    def update(self, dt):
        self.body1.calc_gravitational_force(self.body2)
        self.body1.calc_gravitational_force(self.body3)
        self.body2.calc_gravitational_force(self.body1)
        self.body2.calc_gravitational_force(self.body3)
        self.body3.calc_gravitational_force(self.body1)
        self.body3.calc_gravitational_force(self.body2)

        self.body1.update_velocity_and_position(dt)
        self.body2.update_velocity_and_position(dt)
        self.body3.update_velocity_and_position(dt)


class ThreeBodyProblem(App):
    def build(self):
        sim = ThreeBodySim()
        sim.initialize_sim()
        Clock.schedule_interval(sim.update, .001)
        return sim


if __name__ == '__main__':
    ThreeBodyProblem().run()
