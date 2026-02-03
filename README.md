# ThreeBodyProblem
An Interactive UI that is inspired by the Three Body Problem. The simulation applied Newton's Law of Gravitation to the bodies in the scene. The gravitational constant that is applied is adjusted to be more appropriate for the scale simulated.

A Kivy based UI allows you to add round bodied objects to the screen and edit initial conditions that are applied to the bodies. The initial conditons can be found after adding a physics body. The initial conditions are the following:

**Position** - (x, y) coordinates on the screen with (0, 0) being the center of the screen.<br>
**Velocity** - (x, y) vector that will move the object on the screen in the direction of the the velocity.<br>
**Mass** - The mass of the object that will affect other bodies in the scene.<br>
**Radius** - The radius of the object. This is visual and doesn't affect the simulation.

**Using the simulation**

Adding objects to the scene can be done with the "**Add Physics Body**" button at the bottom center of the screen. This will add an object to a random coordinate on the screen with a random velocity

Starting and stopping the simulation can be doen with the "**Play/Pause**"  button at the bottom right of the screen. Hitting "Play" will start the simulation. Hitting "Pause" will reset the scene back to  the original conditions of the scene.

Editing initial values of the scene is done by entering numerical values in the text field that appears after adding a physics body.