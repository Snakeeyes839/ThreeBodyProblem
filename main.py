import logging

from kivy.config import Config

Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import random


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

MIN_POS_X, MAX_POS_X = -500, 500
MIN_POS_Y, MAX_POS_Y = -300, 300
MIN_VEL_X, MAX_VEL_X = -100, 100
MIN_VEL_Y, MAX_VEL_Y = -100, 100
MIN_R, MAX_R = 1, 50
MIN_M, MAX_M = 10, 100000

# Later add adjusting UI so more fit of the screen
MAX_ON_SCREEN = 6


# Input is restricted to numeric, but we still need to account for null or '-'
def to_int(value):
    if value == '-' or value == '':
        return 0
    else:
        return int(value)


def rearrange_ui(bodies):
    for i in range(len(bodies)):
        bodies[i].ui.grid.pos = (10, Window.height - (bodies[i].ui.grid.height * (i + 1)))


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

    def set_initial_conditions(self, ui_info):
        mass   = abs(to_int(ui_info.mass.text))
        radius = abs(to_int(ui_info.radius.text))

        # To avoid any zero mass that would cause divide by zero error
        if mass == 0:
            mass = 1

        # To avoid any render issues
        if radius == 0:
            radius = 1

        init_v = (to_int(ui_info.velocity_x.text), to_int(ui_info.velocity_y.text))

        x = (Window.width / 2) + to_int(ui_info.position_x.text)
        y = (Window.height / 2) + to_int(ui_info.position_y.text)

        self.mass = mass
        self.size = (2*radius, 2*radius)
        self.velocity = init_v
        self.center = (x, y)

    def calc_gravitational_force(self, exerting_body):
        # G = 6.6743e−11
        G = 6.6743

        # Newton's Law of Universal Gravitation in Vector Form
        # Fg = -G * (m1m2 / |r_21|^3) * r_21
        # gravitation_force is added to the new force here because if there is more than two bodies in the simulation
        # then we need to add the totals up. But at the end of update_velocity_and_position we reset the total
        # gravitational_force to zero to recalculate gravity based on the new positions
        m1m2 = self.mass * exerting_body.mass
        b1b2_displacement = Vector(self.center) - Vector(exerting_body.center)
        b1b2_magnitude = b1b2_displacement.length()

        # In the event that two object are occupying the same space nudge them along
        if b1b2_magnitude == 0:
            b1b2_magnitude = 1

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
    bodyUI = []
    add_button = ObjectProperty(None)

    is_paused = True

    def initialize_sim(self):
        add_button = self.add_btn
        play_btn   = self.play_btn
        add_button.bind(on_press=self.add_callback)
        play_btn.bind(on_press=self.pause_play_callback)

    def update(self, dt):
        if not self.is_paused:
            # Applied Bodies
            for applied_body in self.bodies:
                # Exerting Bodies
                for exerting_body in self.bodies:
                    if applied_body is not exerting_body:
                        logging.debug('Calculating gravity for applied body {0} from exerting body {1}'.format(applied_body, exerting_body))
                        applied_body.calc_gravitational_force(exerting_body)
                    else:
                        logging.debug('Skipping gravity of {0} from {1}. Dont apply gravity to self'.format(applied_body, exerting_body))

            for body in self.bodies:
                logging.debug('Updating velocity and position')
                body.update_velocity_and_position(dt)
        else:
            for i in range(len(self.bodies)):
                self.bodies[i].set_initial_conditions(self.bodies[i].ui)

    def add_callback(self, event):
        count = len(self.bodies)

        # Later add adjusting UI so more fit of the screen
        if count >= MAX_ON_SCREEN:
            return

        window_h_center = Window.height / 2
        window_w_center = Window.width / 2

        self.bodies.append(ObjectProperty(None))

        # Randomly get Object parameters
        position_x = random.randint(MIN_POS_X, MAX_POS_X)
        position_y = random.randint(MIN_POS_Y, MAX_POS_Y)
        velocity_x = random.randint(MIN_VEL_X, MAX_VEL_X)
        velocity_y = random.randint(MIN_VEL_Y, MAX_VEL_Y)
        radius = random.randint(MIN_R, MAX_R)
        mass = random.randint(MIN_M, MAX_M)

        x = window_w_center + position_x
        y = window_h_center + position_y

        body = PhysicsBody(pos=(x, y), size=(2*radius, 2*radius))
        body.ui.grid.pos = (10, Window.height - (body.ui.grid.height * (count+1)))

        # Add the widget to the sim and to the list of bodies
        self.add_widget(body)
        self.bodies[count] = body

        # Set the UI to display Object parameters
        body.ui.position_x.text = str(position_x)
        body.ui.position_y.text = str(position_y)
        body.ui.velocity_x.text = str(velocity_x)
        body.ui.velocity_y.text = str(velocity_y)
        body.ui.mass.text   = str(mass)
        body.ui.radius.text = str(radius)

        body.set_initial_conditions(body.ui)

        # Bind the delete button
        body.ui.delete_btn.bind(on_press=lambda event: self.delete_object_callback(event, body, self.bodies))

        # Without this the ellipse physics bodies don't appear for some reason
        self.add_widget(Label(text=""))

    def pause_play_callback(self, event):
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.play_btn.text = 'Play'
        else:
            self.play_btn.text = 'Pause'

    def delete_object_callback(self, event, body, bodies):
        self.remove_widget(body)
        if body in bodies:
            bodies.remove(body)
            rearrange_ui(bodies)


class ThreeBodyProblem(App):
    def build(self):
        sim = ThreeBodySim()
        sim.initialize_sim()
        Clock.schedule_interval(sim.update, .001)
        return sim


if __name__ == '__main__':
    ThreeBodyProblem().run()
