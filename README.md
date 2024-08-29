<p align="center" style="margin-bottom: 10px;">
      <img src="https://i.ibb.co/YbtktKX/pyth-finder-logo.png" alt="pyth-finder-logo" border="0">
</p>

![version_badge](https://img.shields.io/badge/alpha-0.0.5-006400)
![license](https://img.shields.io/badge/license-MIT-62e39e)

<br />

# Installation
Before we dive into it, make sure you have:
* a ``Python`` version greater than 3.10 ([latest version][1] is recommended);
* [``pip``][2] installed on your device (usually pip3 for 3.x versions, but pip works too);
* our team's ``font`` '[graffitiyouthregular][5]' installed on your machine (used on the interface);
<br />

Now the installation it's as easy as writing a command in the command prompt or in Visual Studio's terminal:

<br/>

<p align="center">
      <img src="https://github.com/omegacoreFLL/PythFinder/assets/159171107/1734dba9-d9a7-4ad4-a3d9-1485a205c082" width = 100% alt="pyth-finder-install" border="0">
</p>

<br />


# Description
``PythFinder`` was developed by team [Omega Core][6] in the scope of enhancing motion planning for the First Lego League competition. 

Usually teams use blocks for coding their autonomous routines because of the lack of ``micropython / python`` documentation online.
This approach may be faster to compile, but it sacrifices reliability.

With this in mind, we chose micropython as the main language to run on our ``EV3`` brick. Throughout the 2023-2024 [Masterpiece][8] season, we experimented with on-the-go motion calculations and concluded that they were **way too slow** for competitive usage. As a result, our focus shifted more toword pre-calculated motion (also known as [feedforward control][9]).

Because [``LEGO®``][10] allowed bricks' processors aren't capable of doing fast calculations, creating a script that would do just that seemed to be the way.

<br/>
<br/>

So we developed a ``trajectory generator tool`` that runs locally on your machine and generates a .txt file with all the necessary information for the robot to mimic the desired movements. You just need to copy the generated text into the robot's code folder to be read during the initialization.

On the robot side, there is a simplified version of just the following aspect of the library, along with methods to construct
trajectories back from the ``.txt`` file decomposition. 

Because of this operation, after starting the program, for an average max-points scoring code, there will be a time window of 1 - 3 minutes when the robot loads all the data (assuming 7-8 different launches). At this time, the code won't be accessible.
Obviously, the time needed for reading data depends on the data amount, which can be manipulated by the user in multiple ways we'll describe later.
**We recommend that you start the program at least 4 minutes before the match.**

But '*why would this method be better?*' you might ask. The answer is **consistency**. This library uses techniques found in industrial robotics control systems, enhancing precision through acceleration limitation profiles, multithreading actions for running multiple motor outputs at the same time, and more.

It's a small price to have one of the most reliable autonomous programs in the FLL competition.

<br/>
<br/>

To clarify, this library is **NOT EV3 dependent**, even though we developed it on this type of brick. Because the hardware is separated from this library, ``SPIKE PRIME`` or ``NXT`` robots can still benefit from the .txt file. The chosen method for uploading data to the robot is versatile, making it compatible with any microprocessor capable of reading from a .txt file, thus can be used outside the FLL competition.

For now, we have a plug-and-play implementation **ONLY** for EV3 robots [pythfinder-quick-start][11], other bricks would need custom implementation of the reading and using of the data. We also recommend running the code for all launches in one program to not deal with loading and waiting in the match.

If you need help with this implementation, think of any improvements or just want to know more about the project, contact us on our Instagram ([@omega.core][12]). We would love to help! 

We would like to create a ``quick-start`` for every FLL-legal brick. A ``SPIKE PRIME`` version will come out around the launch of the **Sumerged** season. If you want to **collaborate with us** on this project by any means, don't hesitate to contact us. 💚🤍

<br/>

# Usage

To start using this library in your environment, simply create a new python file and import the library:

```python
import pythfinder
```

## Create a Robot
To enable any robot-visualization elements of the library, you need to create a '*Simulator*' object. This class encapsulates every separate component into one big control center, taking care of the pygame window display, joystick input, and other pygame events (see [*Advanced Usage*](#advanced-usage)).

```python
sim = pythfinder.Simulator()
```

<br />

This would create a simulator with *default* constants. To override them, simply create a '*Constants*' object with your desired values and pass it to the constructor:

```python 
# pass your values here
custom_constants = pythfinder.Constants(...) 

sim = pythfinder.Simulator(custom_constants)
```


Every time you run the simulator, it'll start with your dataset of constants. You'll learn another way to change constants in the [*Interface Settings*](#interface-settings) section.

<br />

Finally, display your simulation:

```python
while sim.RUNNING():
    sim.update()
```

<br/>

<p align="center">
      <img src="https://i.ibb.co/CKtP4wg/first-impresion.png" width = 100% alt="pyth-finder-joystick" border="0">
</p>


The code runs until you exit the simulator window. Connecting a [*supported controller*](#joystick-control) will allow you to move freely on the field.

## Joystick Control

PythFinder is built on top of pygame's functionalities, from which it inherits support for XBOX, PS4, and PS5 controllers.

Connecting them is as easy as plugging in the **USB** or connecting it via **Bluetooth**. The simulator will recognize it most of the time;  otherwise, it'll raise an error.

All of the Nintendo controllers are currently not supported and will raise an error.

As of version 0.0.5.0-alpha, the latest release introduces enhanced functionality for controlling settings, robot movement not included. In addition to the existing controller-based controls, users can now also utilize keyboard buttons to access and operate most of the functionalities previously limited to the controller interface.

The controls used to manipulate the simulator are the following:
<br />
<span style="font-size:0.8em;">*(the order of buttons is: **ps4 / xbox / keyboard**)*</span>
* ``△ / Y`` <span style="font-size:0.8em; color: darkgreen">*or*</span> ``SPACE`` **--** go forwards / backwards (when field centric is on);
* ``□ / X`` <span style="font-size:0.8em; color: darkgreen">*or*</span> ``ESCAPE`` **--** enter / exit interface setting menu;
* ``○ / B`` <span style="font-size:0.8em; color: darkgreen">*or*</span>  ``TAB`` **--** reset robot pose to origin / press buttons (when the menu is activated);
* ``X / A`` <span style="font-size:0.8em; color: darkgreen">*not keyboard accessible*</span>  **--** show / hide trail;
* ``left bumper`` <span style="font-size:0.8em; color: darkgreen">*or*</span> ``DELETE`` **--** erase trail / set values to default (when the menu is activated);
* ``right bumper`` <span style="font-size:0.8em; color: darkgreen">*not keyboard accessible*</span> **--** when held, enters selection mode;
* ``D-pad`` <span style="font-size:0.8em; color: darkgreen">*or*</span> ``ARROWS`` **--** move through the interface menu / select the robot's orientation (when selection mode is on);
* ``left joystick`` <span style="font-size:0.8em; color: darkgreen">*not keyboard accessible*</span> **--** control robot's linear velocity + angular velocity (when field centric is on);
* ``right joystick`` <span style="font-size:0.8em; color: darkgreen">*not keyboard accessible*</span> *--* control angular velocity (**ONLY** when field centric is off);
* ``options / start`` <span style="font-size:0.8em; color: darkgreen">*or*</span> ``S`` **--** take a screenshot (found in the 'Screenshots' folder inside the locally installed library location);

<br/>

<p align="center">
      <img src="https://github.com/omegacoreFLL/PythFinder/assets/159171107/7be00ab0-aa3b-433c-968d-4bc78f33f0b3" width = 100% alt="pyth-finder-joystick" border="0">
</p>

## Trajectory Usage

### What are Trajectories?

First, we define a specific set of data regarding the robot's position, speed, and distance traveled as a **state of motion**.

Multiple states of motion that exhibit certain similarities are referred to as **motion segments**. These segments are further categorized based on their *complexity*. `Primitives` denote movements with a single degree of freedom (1D), such as pure rotation, pure linear movement, or even stationary states (waiting). These primitives serve as building blocks for `complex` segments, which incorporate two or more primitives and characterize movements with two or three degrees of freedom, primarily intended for *omnidirectional* robots. For For FLL purposes, you'll mostly use primitives, but any motion segment adapts automatically to the chassis used.

Ultimately, all motion segments and auxiliary elements that perform various functions (e.g., other motors usage), known as *markers*, collectively constitute a *`trajectory`*.

<br/>

### How to Create Trajectories

Trajectories are constructed using the '**TrajectoryBuilder**' class. This class requires a *Simulator* object as a parameter, and optionally, a `starting position` and a `preset` to use. By default, the initial position is set at the origin of the Cartesian coordinate system.

The constructor offers intuitive methods for crafting precise trajectories, incorporating personalised **motion** functions. These functions are engineered to accommodate both omnidirectional and unidirectional robots.

The constructor identifies the type of chassis in use and **adjusts** the provided functions accordingly, as certain chassis types may have physical limitations that render some movements **impossible**. By default, non-holonomic chassis are `tangent` to the trajectory, whereas holonomic chassis are given the option to `interpolate` orientation.

Here is a list of available motion functions:
* *`wait()`*
* *`inLineCM()`*
* *`turnToDeg()`*
* *`toPoint()`* <span style="font-size:0.8em; color: darkgreen">*or*</span> 
  *`toPointTangentHead()`*
* *`toPose()`* <span style="font-size:0.8em; color: darkgreen">*or*</span>
  *`toPoseTangentHead()`* <span style="font-size:0.8em; color: darkgreen">*or*</span>
  *`toPoseLinearHead()`*

<br/>

### What are Markers?

These functionalities can be integrated with **markers**, facilitating the management of parallel tasks that are independent of the robots' movement by employing `multithreading` techniques. Markers can be configured to activate after a certain **`time`** period or **`distance`**, either **`relative`** to the last motion function or **`absolute`** with respect to the start of the trajectory.
<br/>

The library also includes special types of markers:
* <span style="color: darkgreen">**`interrupts`**</span>: Disrupt the trajectory's continuity at the specified moment, based on time or distance. Think of interrupts as the sudden braking of a car;
* <span style="color: darkgreen">**`dynamic constraints`**</span>: Allow you to modify portions of the trajectory to operate at different speeds without sacrificing continuity.

Here is a list of all markers:
* *`interruptTemporal()`* <span style="font-size:0.8em; color: darkgreen">*or*</span> *`interruptDisplacement()`*
* *`addTemporalMarker()`* <span style="font-size:0.8em; color: darkgreen">*or*</span> *`addDisplacementMarker()`*
* *`addRelativeTemporalMarker()`* <span style="font-size:0.8em; color: darkgreen">*or*</span> *`addRelativeDisplacementMarker()`*
* *`addRelativeTemporalConstraints()`* <span style="font-size:0.8em; color: darkgreen">*or*</span> *`addRelativeDisplacementConstraints()`*

<br/>
`Interrupts` and `Constraints` are **strictly** relative, as we have observed that users find it **difficult** to visualize the trajectory segments to which they apply. They modify the trajectory's course itself, as opposed to markers that call functions and might adversely affect the trajectory's construction. However, if users **request**, I will reintroduce these functionalities, as they were included in the library's initial prototypes.

Markers can also include **negative** values, which are interpreted as relative to the end of the trajectory or motion segment, while **positive** values are interpreted as relative to the beginning of these elements.

<br/>

### Example

After specifying the desired motion, the *`.build()`* function must be called to compute the trajectory values.

Putting it all together, we obtain:

```python
# first launch from our Masterpiece code

START_POSE = Pose(-47, 97, -45)
PRESET = 1

trajectory = (TrajectoryBuilder(sim, START_POSE, PRESET)
              .inLineCM(75)
                    .addRelativeDisplacementMarker(35, lambda: print('womp womp'))
                    .addRelativeDisplacementMarker(-12, lambda: print('motor goes brr'))
                    .addRelativeDisplacementConstraints(cm = 30, 
  						constraints2d = Constraints2D(linear = Constraints(
                                                               vel = 10, 
                                                               dec = -50)))                                                   
                    .addRelativeDisplacementConstraints(cm = 36, 
  						constraints2d = Constraints2D(linear = Constraints(
 										   vel = 27.7, 
                                                               acc = 35, 
                                                               dec = -30)))
                    .interruptDisplacement(cm = 66)
              .wait(2600)
                    .addRelativeTemporalMarker(-1, lambda: print('motor goes :('))
              .inLineCM(-30)
              .turnToDeg(90)
              .inLineCM(-20)
              .turnToDeg(105)
              .inLineCM(-47)
              .turnToDeg(20)
              .wait(ms = 1200)
                    .addRelativeTemporalMarker(0, lambda: print("spin'n'spin'n'spin.."))
                    .addRelativeTemporalMarker(-1, lambda: print("the party's over :("))
              .turnToDeg(80)
              .inLineCM(-120)
              .build())
```

## Trajectory Visualisation

After creating your trajectory, call the '*.follow()*' method and pass the '**Simulator**' object to see your code in action!

This method takes as an optional parameter the following type as a boolean:
* <span style="color: lightgreen">*``perfect``*</span> **=** simulator iterates through each motion state and displays the robot in the pre-calculated position. For this mode, you can also change the step size in which the list is iterated. A bigger step size means a faster robot on screen.
* <span style="color: lightgreen">*``real``*</span> **=** simulator gives the calculated powers to the robot object, which looks exactly like it would run in real time. This mode is **recommended** for better visualization.

The last optional parameter is '*wait*'. When this boolean is set to True, it waits until the simulator is fully rendered on the user's screen before proceeding with the trajectory. This is useful when perfect following and a big step number are set, it makes you be able to see even the start. Our fifth run looks something like this:

```python
# default values
PERFECT_STEPS = 40
PERFECT_FOLLOWING = False
WAIT = True 

trajectory.follow(sim, PERFECT_FOLLOWING, WAIT, PERFECT_STEPS)
```
<br/>

<p align="center">
      <img src="https://github.com/omegacoreFLL/PythFinder/assets/159171107/2449776e-9608-4199-a631-119ef2d28aa1" width = 100% alt="pyth-finder-traj-follow" border="0">
</p>

## Velocity Graph

To facilitate the understanding of the 'trajectory' concept, I have implemented an easy-to-use graphical visualization method for motion profiles.

I truly believe that this library represents one of the best ways to begin learning the concepts **used in industry**, aiming to assist and inspire future engineers and programmers!

Calling the *`.graph()`* function will display a Matplotlib graph of the **velocity** and **acceleration** for the left and right wheels. There are also optional parameters to display each value separately. Additionally, users can choose whether they want to view the velocity and acceleration of the wheels or the chassis.

An interesting aspect is the *`connect`* parameter. By default, it is set to True, causing lines to be drawn between points. Setting it to False reveals discontinuities (in acceleration, as velocity is optimized for continuity).

```python
# default values
CONNECT = True
VELOCITY = True
ACCELERATION = True
WHEEL_SPEEDS = True

trajectory.graph(CONNECT, VELOCITY, ACCELERATION, WHEEL_SPEEDS)
```
<br/>

<p align="center">
      <img src="https://i.ibb.co/V2Ts2QG/simulator-trajgraph.png" width = 100% alt="pyth-finder-graph" border="0">
</p>

## Generate Velocities

To actually make the robot move like in the simulator, you'll need to **transfer** the data through a '.txt' file. This is accomplished with the '.generate()' method. Just pass the text file name / path and the step size:

```python
STEPS = 6
FILE_NAME = 'test'
WHEEL_SPEEDS = True
SEPARATE_LINES = False

trajectory.generate(FILE_NAME, STEPS, WHEEL_SPEEDS, SEPARATE_LINES)
```

Now you can copy the '.txt' file and load it into the quick-start to see it running!
<br/>

<p align="center">
      <img src="https://i.ibb.co/8BBsxFF/traj-generator.png" width = 100% alt="pyth-finder-generate" border="0">
</p>

## Interface Settings

There are two main ways you can manipulate your simulator environment through constants.

The first way is to simply pass a new instance of '**Constants**' when creating the sim object, changing any of the following values:

```python 
# constants.py -- simplification

# all modifiable values:
class Constants():
def __init__(self, 
                 pixels_to_dec,
                 fps,
                 robot_img_source,
                 robot_scale,
                 robot_width,
                 robot_height,
                 text_color,
                 text_font,
                 max_trail_len,
                 max_trail_segment_len,
                 draw_trail_threshold,
                 trail_color,
                 trail_loops,
                 trail_width,
                 background_color,
                 axis_color,
                 grid_color,
                 width_percent,
                 backing_distance,
                 arrow_offset,
                 time_until_fade,
                 fade_percent,
                 real_max_velocity,
                 max_power,
                 
                 screen_size,
                 constraints2d,
                 kinematics):
    ...
```

As described in the [Create a Robot](#create-a-robot) section, these changes will be automatically applied at the start of the simulation. For an in-depth explanation of the constants, see the [documentation](#advanced-usage).

The second way is through the interface menu (**NOT FULLY IMPLEMENTED YET**) with joystick control. This is a more 'on-the-go' change and will reset every time you restart the simulator.
<br/>

<p align="center">
      <img src="https://i.ibb.co/R2HMqKW/simulator-intefacemenu.png" width = 100% alt="pyth-finder-presets" border="0">
</p>

## Presets

A **remarkable innovation** introduced by this library is the feature called `presets`. These allow you to completely transform the interface appearance, robot configuration, and chassis type with the press of a button. You can utilize the number keys from `1` to `9` on the keyboard, each assigned to a distinct set of constants that adjust the simulation in various ways. The `0` key serves to reset the interface to its *default* settings.

Beyond these predefined options, you have the ability to create your **own** custom presets, tailored to your individual needs and preferences. This functionality adds an extra level of **flexibility** and **control** over the configuration of the `interface`, `robot behavior`, and `simulator parameters`.

By default, the button **1** is the latest `FLL` field and the button **2** is the latest `FTC` field:
<br/>

<p align="center">
      <img src="https://github.com/omegacoreFLL/PythFinder/assets/159171107/0ea2aa63-31f7-41cb-b267-3ee00500d26b" width = 100% alt="pyth-finder-presets" border="0">
</p>

## Painting
In response to a community request, we have implemented a new feature that allows users to draw shapes on the screen. This feature proves to be particularly useful when engaging in discussions or explaining strategies to team members or judges.

To access the drawing functionality, simply toggle the `HAND DRAWING` option located in the **Other Menu**. Additionally, users can choose from a variety of colors by selecting the desired color from the color picker in the **Draw Menu**.

Accessing the painting tools can be done using keyboard shortcuts. Simply press the designated keys to activate the desired painting tool:
* `E` **--** *erase tool*;
* `L` **--** *line tool*;
* `R` **--** *rectangle tool*;
* `C` **--** *circle tool*;
* `T` **--** *triangle tool*;
* `ENTER` **--** *exiting tools*;

The functionality is similar to that of a painting program. Accessing different tools **will change the cursor icon**, providing visual feedback to the user regarding the selected tool.

<p align="center">
      <img src="https://i.ibb.co/f1nTKKT/simulator-paint.png" width = 100% alt="pyth-finder-paint" border="0">
</p>




## Advanced Usage

Check out the full [**documentation**][17].


*Credits:*
* *libraries used: [pygame][3], [matplotlib][4], [pybricks][7]*
* *robot photo made with: [studio 2.0][14]*
* *design made with: [illustrator][16]*
* *inspiration: [roadrunner FTC][13]*
* *font: [graffitiyouthregular][5]*
* *fields: [reddit][15]*

<br />


*v. 0.0.5.0-alpha*


[1]: https://www.python.org/downloads/             "python download page"
[2]: https://pip.pypa.io/en/stable/installation/   "pip download page"
[3]: https://www.pygame.org/docs/                  "pygame quick start"
[4]: https://matplotlib.org/stable/                "matplot quick start"
[5]: https://www.dafont.com/graffiti-youth.font    "our team's use-free font"
[6]: https://linktr.ee/omega.core                  "our team's socials"
[7]: https://pybricks.com/ev3-micropython/startinstall.html "pybricks instalation for EV3 robots"
[8]: https://www.first-lego-league.org/en/2023-24-season/the-masterpiece-season "fll masterpiece"
[9]: https://www.youtube.com/watch?v=FW_ay7K4jPE "very well explained feedforward control video"
[10]: https://lego.com "lego official"
[11]: https://github.com/omegacoreFLL/pythfinder-quickstart.git "PythFinder quick start for EV3"
[12]: https://www.instagram.com/omegacoreFLL "instagram link"
[13]: https://github.com/acmerobotics/road-runner "roadrunner"
[14]: https://www.bricklink.com/v3/studio/download.page "lego cad software"
[15]: https://www.reddit.com "field images"
[16]: https://www.adobe.com/ro/products/illustrator.html "adobe illustrator"
[17]: https://github.com/omegacoreFLL/PythFinder/wiki "pythfinder's extended documentation"