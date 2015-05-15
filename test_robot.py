import sys
import time
import serial
from getch import getch, pause
from robot import Robot
if(len(sys.argv) != 2):
  print("Usage: python test_robot.py <serial port> <angle> <stretch>")
  print("Please supply the path of the serial port (for instance /dev/tty.usbserial-A6031W5L)")
  sys.exit(1)

robot = Robot(sys.argv[1])
  
while True:
  try:
     print("\rWaiting for key")
     key = getch.getch()
     if ord(key) == 3:
       sys.exit(0)
     if key == 'p':
       angle = int(raw_input("Angle: "))
       stretch = int(raw_input("Stretch: "))
       robot.pickup(angle, stretch);
     else:
       robot.send_command([ord(key)])
      
  except Exception as e:
    print(e)
  