# ThreeBodyProblem
An Interactive UI that is inspired by the Three Body Problem. The simulation applied Newton's Law of Gravitation to the bodies in the scene. The gravitational constant that is applied is adjusted to be more appropriate for the scale simulated.

A Kivy based UI allows you to add round bodied objects to the screen and edit initial conditions that are applied to the bodies. The initial conditions can be found after adding a physics body. The initial conditions are the following:

**Position** - (x, y) coordinates on the screen with (0, 0) being the center of the screen.<br>
**Velocity** - (x, y) vector that will move the object on the screen in the direction of the velocity.<br>
**Mass** - The mass of the object that will affect other bodies in the scene.<br>
**Radius** - The radius of the object. This is visual and doesn't affect the simulation.

**Using the simulation**

Adding objects to the scene can be done with the "**Add Physics Body**" button at the bottom center of the screen. This will add an object to a random coordinate on the screen with a random velocity

Starting and stopping the simulation can be done with the "**Play/Pause**"  button at the bottom right of the screen. Hitting "Play" will start the simulation. Hitting "Pause" will reset the scene back to  the original conditions of the scene.

Editing initial values of the scene is done by entering numerical values in the text field that appears after adding a physics body.

**Loading Presets**

There are a few preset scenes that are defined in the *presets.xml*.  Loading a preset can be done by clicking one of the preset buttons in the top right corner of the screen. Loading a preset will clear the current scene and add the defined objects.

**Adding Presets**

Currently, the way to add a preset is to edit the *presets.xml*. You must add a preset using the **\<preset>** tag. Inside the **\<preset>** tag the bodies must individually be defined using the **\<body>** tag. The initial conditions of the body must be defined inside the **\<body>** tag.
The initial conditions to be defined are **<position_x>**, **<position_y>**, **<velocity_x>**, **<velocity_y>**, **\<mass>**, and **\<radius>**

The preset buttons are dynamically created on load, and the name defined in the preset tag will appear as the button text in the scene.

**Preset Example:**
```
presets.xml

<presets>
    <preset name="Preset Test">
        <body>
            <position_x>0</position_x>
            <position_y>0</position_y>
            <velocity_x>0</velocity_x>
            <velocity_y>0</velocity_y>
            <mass>100000</mass>
            <radius>20</radius>
        </body>
        <body>
            <position_x>100</position_x>
            <position_y>0</position_y>
            <velocity_x>0</velocity_x>
            <velocity_y>-80</velocity_y>
            <mass>100</mass>
            <radius>5</radius>
        </body>
    </preset>
<presets>```