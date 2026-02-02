import logging
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable(logging.DEBUG)


class BodyUI(Widget):
    pass


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

        assert b1b2_magnitude != 0, "Displacement should not be zero"

        self.gravitational_force = (-G * (m1m2 * b1b2_displacement) / (b1b2_magnitude ** 3)) + self.gravitational_force

    def update_velocity_and_position(self, delta_time):
        # Convert Force vector applied by gravity to velocity
        self.velocity = ((Vector(*self.gravitational_force) / self.mass) * delta_time) + self.velocity

        # Convert velocity into position
        self.center = (Vector(*self.velocity) * delta_time) + self.center

        # Reset the gravitational_force since positions have changed, thus changing the gravitational effects
        self.gravitational_force = [0, 0]


class ThreeBodySim(Widget):
    bodies = []
    bodyUI = ObjectProperty(None)
    add_button = ObjectProperty(None)

    click = 0

    def initialize_sim(self):
        window_h_center = Window.height / 2
        window_w_center = Window.width / 2

        r1 = 5
        r2 = 40
        r3 = 5

        #self.bodies[0] = PhysicsBody(pos=(window_w_center + 100 - r1, window_h_center - r1), size=(2*r1, 2*r1))
        #self.bodies[1] = PhysicsBody(pos=(window_w_center - r2, window_h_center - r2), size=(2*r2, 2*r2))
        #self.bodies[2] = PhysicsBody(pos=(window_w_center - 100 - r3, window_h_center - r3), size=(2*r3, 2*r3))

        #self.bodies[0].set_initial_conditions(200, Vector(0, -30))
        #self.bodies[1].set_initial_conditions(100000, Vector(0, 0))
        #self.bodies[2].set_initial_conditions(200, Vector(0, 30))

        #self.add_widget(self.bodies[0])
        #self.add_widget(self.bodies[1])
        #self.add_widget(self.bodies[2])

        add_button = self.btn1
        add_button.bind(on_press=self.button_callback)

    def update(self, dt):

        if self.click >= 3:
            # Applied Bodies
            for i in range(len(self.bodies)):
                # Exerting Bodies
                for j in range(len(self.bodies)):
                    if i is not j:
                        logging.debug('Calculating gravity for applied body {0} from exerting body {1}'.format(i, j))
                        self.bodies[i].calc_gravitational_force(self.bodies[j])
                    else:
                        logging.debug('Skipping gravity of {0} from {1}. Dont apply gravity to self'.format(i, j))

            for body in self.bodies:
                logging.debug('Updating velocity and position')
                body.update_velocity_and_position(dt)

    def button_callback(self, event):
        window_h_center = Window.height / 2
        window_w_center = Window.width / 2

        self.bodies.append(ObjectProperty(None))

        self.bodies[self.click] = PhysicsBody(pos=(window_w_center + 50*self.click, window_h_center), size=(10, 10))
        self.bodies[self.click].set_initial_conditions(200, Vector(0, -30 * self.click))

        self.add_widget(self.bodies[self.click])

        logging.debug(len(self.bodies))

        self.click += 1

    # def on_touch_down(self, touch):
    #     if self.click < 3:
    #         self.bodies[self.click].center = touch.pos
    #         self.click = self.click + 1


class ThreeBodyProblem(App):
    def build(self):
        sim = ThreeBodySim()
        sim.initialize_sim()
        Clock.schedule_interval(sim.update, .001)
        return sim


if __name__ == '__main__':
    ThreeBodyProblem().run()
