from cam import CameraProcessor
import sys

if (len(sys.argv) < 2):
  sys.exit("Please supply camera number (probably 0 or 1)")

processor = CameraProcessor(int(sys.argv[1]))
processor.callibrate()
processor.main()