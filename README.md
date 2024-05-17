![pyth_finder_logo](https://github.com/omegacoreFLL/PythFinder/assets/159171107/1dc439b2-0ac0-40f8-95fd-4883b0507603)

![version_badge](https://img.shields.io/badge/alpha-0.0.3-006400)
![license](https://img.shields.io/badge/license-MIT-62e39e)

<br />
<br />

# Instalation
Before we dive into it, make sure you have:
* a python version greater than 3.10 ([latest version][1] is recommended).
* [pip][2] installed on your device (usually pip3 for 3.x versions, but pip works too).
<br />

Now the instalation it's as easy as writing a command in the command prompt or in Visual Studio's terminal:

```bash
pip install pythfinder
```
or (on most devices):

```bash
pip3 install pythfinder 
```
<br />
<br />


# Description
PythFinder was developed by team [Omega Core][6] in the scope of enhancing motion planning for the First Lego League competition. 

Usually teams use blocks for coding their autonomus routines, because of the lack of micropython / python documentation online.
This approach may be faster compiling, but it sacrifices reliability.

With this in consideration, we chose micropython as the main language to run onto our EV3 brick. Throughout the 2023-2024 [Masterpiece][8] season we experimented on-the-go motion calculations and concluded that it was **way to slow** for competitive usage. As a result, our focus shifted more onto pre-calculated motion (also known as [feedforward control][9]).

Because [LEGO®][10] allowed bricks' processors aren't capable of doing fast calculations, creating a script that would do just that seemed to be the way.

<br/>
<br/>

So we developed a **trajectory generator tool**, which runs localy on your machine and generates a .txt file with all the necessary information for the robot to mimic the desired movements. You just need to copy the generated text into the robot's code folder to be read on the initialization.

On the robot side, there is a simplified version of just the following aspect of the library, along with methods to construct
trajectories back from the .txt file decomposition. 

Because of this operation, after starting the program, for an average max-points scoring code, there will be a time window of 2 - 5 minutes, when the robot loads all the data (assuming 7-8 different launches). In this time, the code won't be accessible.
Obviously, the time needed for reading data depents on the data amount, which can be manipulated by the user in multiple ways we'll describe later.
**We recommend you to start the program with at least 5 minutes before the match.**

But '*why would this method be better?*' you might ask. The answear is **consistency**. This library uses techniques found in industrial robotics control systems, enhancing the precision through acceleration limitation profiles, multithreading actions for running multiple motor outputs at the same time and more.

It's a small price to have one of the most reliable autonomus programs in the FLL competition.

<br/>
<br/>

To clarify, this library is **NOT EV3 depentent**, even though we developed it on this type of brick. Because the hardware is separated from this library, SPIKE PRIME or NXT robots can still benefit from the .txt file.

For now, we have a plug-and-play implementation **ONLY** for EV3 robots [pythfinder-quick-start][11], other bricks would need custom implementation of the reading and using of the data. We also recommend running the code for all launches in one program, to not deal with loading waiting in the match.

If you need help in this implementation, contact us on our instagram ([@omega.core][12]), we would love to help! 

We would like to create a quick-start for every FLL-legal brick, but we don't have any besides EV3 at the moment, to be able to do tests. If you want to **colaborate with us** in this project by any means, don't hesitate to contact us. 💚🤍

<br/>
<br/>

# Usage

To start using this library in your environment, simply create a new python file and import the library:

```python
import pythfinder
```

## Create a Robot
To enable any robot-visualisation elements of the library, you need to create a '*Simulator*' object. This class encapsulates every separate component into one big control-center, taking care of the pygame window display, joystick input and other pygame events (see [*Advanced Usage*](#advanced-usage)).

```python
sim = pythfinder.Simulator()
```

<br />

This would create a simulator with *default* constants. To override them, simply create a '*Constants*' object with your desired values and pass it to the constructor:

```python 
#pass your values here
custom_constants = pythfinder.Constants(...) 

sim = pythfinder.Simulator(custom_constants)
```


Everytime you run the simulator it'll start with your dataset of constants. You'll learn another way to change constants in the [*Interface Settings*](#interface-settings) section.

<br />

Finally, display your simulation:

```python
while sim.RUNNING():
    sim.updade()
```

The code runs until you exit the simulator window. Connecting a [*supported controller*](#joystick-control) will allow you to move freely on the field.

## Joystick Control

PythFinder is built on top of pygame's functionalities, from which it inherits support for XBOX, PS4 and PS5 controllers.

Connecting them is as easy as plugging in the **USB** or connecting it via **Bluetooth**. The simulator will recognize it most of the times, otherwise will raise an error.

All of the Nintento controllers are currently not supported and will raise an error.

The controls used to manipulate the simulator are the following:
<br />
<span style="font-size:0.8em;">*(the order of buttons is: **ps4 / xbox**)*</span>
* <span style="color: lightgreen">△ / Y</span> **--** go forwards / backwards (when field centric is on) ;
* <span style="color: lightgreen">□ / X</span> **--** enter / exit interface setting menu ;
* <span style="color: lightgreen">○ / B</span> **--** reset robot pose to origin / selects buttons (when the menu is activated) ;
* <span style="color: lightgreen">X / A</span> **--** show / hide trail ;
* <span style="color: lightgreen">left bumper</span> **--** erase trail / sets values to default (when the menu is activated) ;
* <span style="color: lightgreen">right bumper</span> **--** when held enters selection mode ;
* <span style="color: lightgreen">D-pad</span> **--** move through interface menu / select robot's orientation (when selection mode is on) ;
* <span style="color: lightgreen">left joystick</span> **--** controls robot linear velocity + angular velocity (when field centric is on) ;
* <span style="color: lightgreen">right joystick</span> -- controls angular velocity (**ONLY** when field centric is off) ;

## Create a Trajectory

Trajectory building is the main feature on our library. Although it's implementation is complicated (see the [documentation](#advanced-usage)), it's usage is trivialy simple.

<span style="font-size:1.5em;">*What are trajectories?*</span> <br />
Firstly, we define a particular set of robot information (like the pose, velocity, distance traveled etc.) as a '**MotionState**'. Multiple motion states sharing a specific similarity are called '**MotionSegments**'. With the same logic in mind, multiple motion segments compose e '**Trajectory**'.

Trajectories are constructed using the '**TrajectoryBuilder**' class. This takes, as optional parameters, a *start_pose* and a *constants*. By default, the starting pose is at the origin of the cartesian system.

The builder has intuitive methods for accomplishing a desired, simple trajectory. This includes **motion** functions:
* *inLineCM()* ;
* *wait()* ;
* *toPoint()* ;
* *toPose()* ;

These can be combined with **markers**, allowing
parallel task managing, utilising multithreading.
Markers can be set by *time* or *distance*, **relative** to the last motion function, or **absolute**, relative to the start of the trajectory.

The library also includes special types of markers:
* **interruptors**: breaks the continuity of the trajectory at the specified point in time / distance. Imagine interruptors as sudden brakes made by a car.
* **dynamic constrains**: allow you to modify portions of the trajectory to run at different speeds, without sacrificing continuity.

A list of all the markers:
* *interruptTemporal()* <span style="font-size:0.8em; color: lightgreen">*or*</span> *interruptDisplacement()* ;
* *addConstrainsTemporal()* <span style="font-size:0.8em; color: lightgreen">*or*</span> *addConstrainsDisplacement()* ;
* *addTemporalMarker()* <span style="font-size:0.8em; color: lightgreen">*or*</span> *addDisplacementMarker()* ;
* *addRelativeTemporalMarker()* <span style="font-size:0.8em; color: lightgreen">*or*</span> *addRelativeDisplacementMarker()* ;

And other uncategorized methods:
* *setPoseEstimate()* ;
* *turnDeg()* ;

which are neither motion functions or markers.

After specifying the desired motion, the '*.build()*' method needs to be called to compute a trajectory. 
<br />
Putting it all together, we get:

```python
# example from our Masterpiece first run code

START_POSE = Pose(-47, 97, -45)
START_CONSTRAINS = Constrains(vel = 27.7, acc = 27.7, dec = -27.7)

trajectory = (TrajectoryBuilder(START_POSE, START_CONSTRAINS)
              .inLineCM(75)
                    .addRelativeDisplacementMarker(35, lambda: print('womp womp'))
                    .addRelativeDisplacementMarker(-12, lambda: print('motor goes brr'))
                    .addConstrainsRelativeDisplacement(start = 30, constrains = Constrains(vel = 10, dec = -50))
                    .addConstrainsRelativeDisplacement(start = 36, constrains = Constrains(vel = 27.7, acc = 35, dec = -30))
                    .interruptDisplacement(66)
              .wait(2600)
                    .addRelativeTemporalMarker(-1, lambda: print('motor goes :('))
              .inLineCM(-30)
              .turnDeg(90)
              .inLineCM(-20)
              .turnDeg(105)
              .inLineCM(-47)
              .turnDeg(20)
              .wait(1200)
                    .addRelativeTemporalMarker(0, lambda: print("spin'n'spin'n'spin.."))
                    .addRelativeTemporalMarker(-1, lambda: print("the party's over :<"))
              .turnDeg(80)
              .inLineCM(-120)
              .build())
```

## Trajectory Visualisation

After creating your trajectory, call the '*.follow()*' method and pass the '**Simulator**' object to see your code in action!

This method takes as an optional parameter the following type as a boolean:
* <span style="color: lightgreen">*perfect*</span> **=** simulator iterates through each motion state and displays the robot at the pre-calculated position. For this mode, you can also change the step size in which the list is iterated. Bigger step size = faster robot on screen.
* <span style="color: lightgreen">*real*</span> **=** simulator gives the calculated powers to the robot object, which looks exactly like it would run in real time. This mode is **recommended** for better visualisation.

The last optional parameter is '*wait*'. When this boolean is set to True, it waits until the simulator is fully rendered on the users' screen before proceeding with the trajectory. This is useful when perfect following and a big step number are set, it makes you be able to even the start.

```python
# default values
PERFECT_STEPS = 40
PERFECT_FOLLOWING = False
WAIT = True 

trajectory.follow(sim, PERFECT_FOLLOWING, WAIT, PERFECT_STEPS)
```

## Velocity Graph

For better understanding of the 'trajectory' concept, we decided to implement a user-friendly **graphical visualisation** of the profiles used, mostly because in FLL teams are lots of youngsters which have just been introduced into robotics.

We really think that this library is one of the best ways to start learning **industrialy-used** concepts, with which we hope to help and inspire future engineers and programmers!

The '*.graph()*' method call will display a matplotlib graph of the left wheel and right wheel **velocities** and **accelerations**. Optional parameters for displaying just one or both are also included.

One neat implementation is the '*connect*' parameter. The default it's set to True, this variable draws lines between points. Setting it to False really shows the discontinuities (in acceleration, because velocity is optimized for continuitiy).

```python
#default values
CONNECT = True
VELOCITY = True
ACCELERATION = True

trajectory.graph(CONNECT, VELOCITY, ACCELERATION)
```

## Generate Velocities

To actually make the robot move like in the simulator, you'll need to **transfer** the data through a '.txt' file. This is accomplished with the '.generate()' method. Just pass the text file name / path and the step size:

```python
STEPS = 6
FILE_NAME = 'test'

trajectory.generate(FILE_NAME, STEPS)
```

Now you can copy the '.txt' file and load it into the quick-start to see it running!

## Interface Settings

There are two main ways you can manipulate your simulator environment through constants.

The first way is simply pass a new instance of '**Constants**' when creating the sim object, changing any of the following values:

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
                 half_unit_measure_line,
                 time_until_fade,
                 fade_percent,
                 screen_size):
    ...
        
```

As described in the [Create a Robot](#create-a-robot) section, these changes will be automatically applied at the start of the simulation. For an in-depth explanation of the constants, see the [documentation](#advanced-usage).

The second way is through the interface menu (**NOT FULLY IMPLEMENTED YET**) with joystick control. This is a more 'on-the-go' change, and will reset everytime you restart the simulator.

## Advanced Usage

Check out the full documentation. --- **TO BE ADDED**


*Credits:*
* *libraries used: [pygame][3], [matplotlib][4], [pybricks][7]*
* *robot photo made with: [studio 2.0][14]*
* *design made with: [illustrator][16]*
* *inspiration: [roadrunner FTC][13]*
* *font: [graffitiyouthregular][5]*
* *table image: [source][15]*

<br />


*v. 0.0.3.17-alpha*


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
[15]: https://www.reddit.com/r/FLL/comments/168hh95/hires_image_of_the_masterpiece_table_3208px_x/ "fll table image"
[16]: https://www.adobe.com/ro/products/illustrator.html "adobe illustrator"