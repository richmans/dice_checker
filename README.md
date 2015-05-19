# The dice checker
My quest to verify dice integrity using the uArm

I was playing a boardgame with some friends, and the game involved two dice. During the game, we noticed that 8 was not thrown
at all, in about 35 turns. We calculated that the chance of this happening is about 1 in 200. So the question is, was this just
an accident, or is something wrong with the dice?

So i thought: Has anyone really checked if every side of this dice has an equal chance of being thrown? 

So to resolve this, i combined the uArm robot with a shoebox and a camera. 

## Components
The uArm is controlled by an arduino, which talks serial to the computer through a usb cable.
The camera is a very old and simple usb webcam which hangs about 20 centimeters above the dice.
I've put some blue paper on the insides of the shoebox, to make some contrast with the dice (which is white)

## Software
I am using opencv SimpleBlobDetector to determine the location of the dice, and HoughCircles to detect the value of each throw. 
In order to make the work of these detectors easier, i use some blurring and thresholding. The SimpleBlobDetector only uses the red 
channel of the camera, which filters out the background very nicely. Using this, the system works in daylight without any
additional lighting.

I use quite a bit of math to translate camera coordinates to real world coordinates. I basically draw a triangle between the two 
callibration points and the detected dice. Then i determine the angles of this triangle. Then i draw a triangle with the same 
angles on the real-world callibration points, and that gives me the real world coordinates of the dice.

## Workflow
To be able to map camera coordinates to real world coordinates, i marked two points on the blue background. When the 
application starts, it shows the camera image, and you have to click the two markers. The application does not try to 
detect the markers in the image. It is only interested in where you click.

To map real world coordinates to robot coordinates, the robot places the dice at a known position, and then the camera analyzes
the position to callibrate.

After these two callibrations, the throwing of dice can begin

- uArm picks up the dice and throws it in the slide.
- camera detects the dice coordinates
- camera detects the score on the dice
- repeat


