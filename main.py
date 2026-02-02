import logging

from kivy.config import Config

#Config.set('graphics', 'fullscreen', 1)
Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import random


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

    def update_initial_conditions(self, ui_info):
        mass = int(ui_info.mass.text)
        radius = int(ui_info.radius.text)
        init_v = (int(ui_info.velocity_x.text), int(ui_info.velocity_y.text))
        init_pos = (int(ui_info.position_x.text), int(ui_info.position_y.text))

        self.mass = mass
        self.size = (radius, radius)
        self.velocity = init_v
        self.center = init_pos

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
    bodyUI = []
    add_button = ObjectProperty(None)

    window_h_center = Window.height / 2
    window_w_center = Window.width / 2
    click = 0

    def initialize_sim(self):

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
                self.bodies[i].update_initial_conditions(self.bodies[i].ui)
            pass

    def button_callback(self, event):
        self.bodies.append(ObjectProperty(None))

        position = [random.randint(1, 1000), random.randint(1, 1000)]
        radius = 20
        mass = 2000
        velocity = [0, 0]

        body = PhysicsBody(pos=(self.window_w_center + position[0] - radius, self.window_h_center + position[1] -
                                radius), size=(2*radius, 2*radius))

        body.set_initial_conditions(mass, Vector(velocity[0], velocity[1]))

        body.ui.grid.pos = (10, Window.height - (150 * (self.click+1)))

        self.add_widget(body)
        self.bodies[self.click] = body

        body.ui.position_x.text = str(position[0])
        body.ui.position_y.text = str(position[1])

        body.ui.velocity_x.text = str(velocity[0])
        body.ui.velocity_y.text = str(velocity[1])

        body.ui.mass.text = str(mass)
        body.ui.radius.text = str(radius)

        # grid = GridLayout(pos=(15, Window.height - 150 * (self.click + 1)), cols=2, spacing=5,
        #                  row_force_default=True, row_default_height=30,
        #                  col_force_default=False, col_default_width=100)
        # Object Position
        # grid.add_widget(Label(text='Position'))
        # pos_box = BoxLayout(orientation='horizontal')
        # pos_box.add_widget(TextInput(text=str(position[0])))
        # pos_box.add_widget(TextInput(text=str(position[0])))
        # grid.add_widget(pos_box)
        # # Object Velocity
        # grid.add_widget(Label(text='Velocity'))
        # vel_box = BoxLayout(orientation='horizontal')
        # vel_box.add_widget(TextInput(text=str(velocity[0])))
        # vel_box.add_widget(TextInput(text=str(velocity[1])))
        # grid.add_widget(vel_box)
        # # Object Mass
        # grid.add_widget(Label(text='Mass'))
        # grid.add_widget(TextInput(text=str(mass)))
        # # Object Radius
        # grid.add_widget(Label(text='Radius'))
        # grid.add_widget(TextInput(text=str(radius)))

        #self.bodyUI.append(grid)

        #self.add_widget(grid)

        # Without this the ellipse physics bodies don't appear for some reason
        self.add_widget(Label(text=""))

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
