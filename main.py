import logging

from kivy.config import Config

Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window

import random
import xml.etree.ElementTree as ET


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


def add_physics_body(bodies, body_params):
    count = len(bodies)

    window_h_center = Window.height / 2
    window_w_center = Window.width / 2

    pos = (window_w_center + body_params.pos_x, window_h_center + body_params.pos_y)
    size = (2*body_params.radius, 2*body_params.radius)

    body = PhysicsBody(pos=pos, size=size)
    body.ui.grid.pos = (10, Window.height - (body.ui.grid.height * (count + 1)))

    # Set the UI to display Object parameters
    body.ui.position_x.text = str(body_params.pos_x)
    body.ui.position_y.text = str(body_params.pos_y)
    body.ui.velocity_x.text = str(body_params.vel_x)
    body.ui.velocity_y.text = str(body_params.vel_y)
    body.ui.mass.text = str(body_params.mass)
    body.ui.radius.text = str(body_params.radius)

    body.set_initial_conditions(body.ui)

    return body


class BodyParameters:
    pos_x = 0
    pos_y = 0
    vel_x = 0
    vel_y = 0
    mass = 1
    radius = 1


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

        # Add preset buttons
        tree = ET.parse('presets.xml')
        root = tree.getroot()
        offset = 1
        for child in root:
            x_offset = Window.width - 65
            y_offset = Window.height - (40 * offset)
            offset += 1
            btn = Button(size=(100, 30), center_x=x_offset, center_y=y_offset, text=child.get('name'))
            btn.bind(on_press=self.load_preset_callback)
            self.add_widget(btn)

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
        # Later add adjusting UI so more fit of the screen
        if len(self.bodies) >= MAX_ON_SCREEN:
            return

        body_params = BodyParameters()

        # Randomly get Object parameters
        body_params.pos_x = random.randint(MIN_POS_X, MAX_POS_X)
        body_params.pos_y = random.randint(MIN_POS_Y, MAX_POS_Y)
        body_params.vel_x = random.randint(MIN_VEL_X, MAX_VEL_X)
        body_params.vel_y = random.randint(MIN_VEL_Y, MAX_VEL_Y)
        body_params.mass = random.randint(MIN_M, MAX_M)
        body_params.radius = random.randint(MIN_R, MAX_R)

        body = add_physics_body(self.bodies, body_params)

        # Bind the delete button
        body.ui.delete_btn.bind(on_press=self.delete_object_callback)

        # Add the widget to the sim and to the list of bodies
        self.add_widget(body)
        self.bodies.append(body)

    def pause_play_callback(self, instance):
        self.is_paused = not self.is_paused

        if self.is_paused:
            instance.text = 'Play'
        else:
            instance.text = 'Pause'

    def delete_object_callback(self, instance):
        # Going to rethink this design, but the 'delete' button's great-grandparent is the base Physics object
        self.remove_widget(instance.parent.parent.parent)
        self.bodies.remove(instance.parent.parent.parent)
        rearrange_ui(self.bodies)

    def load_preset_callback(self, instance):
        # When loading a preset remove the bodies currently loaded
        for b in self.bodies:
            self.remove_widget(b)
        self.bodies.clear()

        tree = ET.parse('presets.xml')
        root = tree.getroot()
        presets = root.findall('preset')

        preset_to_load = None

        for p in presets:
            if p.get('name') == instance.text:
                preset_to_load = p
                break

        if preset_to_load is None:
            logging.debug('Error when finding XML preset: {}'.format(instance.text))
            return

        body_params = BodyParameters()

        for b in preset_to_load.findall('body'):
            body_params.pos_x  = int(b.find('position_x').text)
            body_params.pos_y  = int(b.find('position_y').text)
            body_params.vel_x  = int(b.find('velocity_x').text)
            body_params.vel_y  = int(b.find('velocity_y').text)
            body_params.mass   = int(b.find('mass').text)
            body_params.radius = int(b.find('radius').text)

            body = add_physics_body(self.bodies, body_params)

            # Bind the delete button
            body.ui.delete_btn.bind(on_press=self.delete_object_callback)

            # Add the widget to the sim and to the list of bodies
            self.add_widget(body)
            self.bodies.append(body)


class ThreeBodyProblem(App):
    def build(self):
        sim = ThreeBodySim()
        sim.initialize_sim()
        Clock.schedule_interval(sim.update, .001)
        return sim


if __name__ == '__main__':
    ThreeBodyProblem().run()
