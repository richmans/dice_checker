import os
import sys
import cv2
from camera import CameraProcessor
def next_image(images):
  if len(images) == 0: 
    return (None,None)
  image_name = images.pop()
  file = "images/%s" % image_name
  print("Reading %s" % file)
  return (image_name, cv2.imread(file))
  
  
images = os.listdir("images")
images = [elem for elem in images if elem[0] != '.']

answers = {
  "152f88bd-b3ce-4453-936b-bd1170f38010.jpg":4,
  "167b0002-fd35-4506-9fd7-e8bf7e807b48.jpg":4,
  "191ff9a5-ff19-4942-af04-0cd0c959a296.jpg":1,
  "37e4c671-6fea-43e4-9851-ce7a7061aa0e.jpg":4,
  "3dc2a74b-7b87-4033-a6ed-aa6bace48a66.jpg":3,
  "40c2158a-cff6-41c7-805c-286640088e6b.jpg":1,
  "4992c00f-7f50-40cb-a6c5-cc4ecded09d5.jpg":4,
  "49c18fa1-aa6b-48b8-a89a-20266a9498c2.jpg":3,
  "4e3d2bac-544c-4805-aaae-f782702b8d1e.jpg":5,
  "4ee7617f-40ca-4146-a747-8d08d06394a0.jpg":2,
  "532cf427-15f9-497c-897e-c105a014d375.jpg":3,
  "537087ad-3494-444c-be53-12214416cdd2.jpg":1,
  "550355e7-c316-4641-99af-04207c04ce58.jpg":3,
  "642f0d14-1c39-488c-b12f-c9c0a134d10f.jpg":5,
  "6893f007-26f7-42c6-9759-c386d4547d0b.jpg":4,
  "6cbf88b6-0b1f-4828-b278-e71ea82558b8.jpg":3,
  "8cf7ed37-1845-4dd4-af9b-394f9c28821f.jpg":2,
  "8ddc19c8-bec7-415d-9c27-9e8f6a384177.jpg":5,
  "8ea6b360-2c1a-499b-a596-7cc6351b2106.jpg":3,
  "9a44a10c-9ebf-4819-918b-4baf0361068d.jpg":1,
  "ba192a31-9bff-4caf-b3dd-01c967874074.jpg":6,
  "bff8ad7b-e800-44bc-adbc-89c71b5bd9fa.jpg":6,
  "c76bcaa5-ff05-45d8-a7a2-c4a47f492af4.jpg":2,
  "cb310875-f4b3-47e5-8bfb-66a447ae48e1.jpg":6,
  "d68c8645-5625-42ca-9335-5548fb94160d.jpg":4,
  "df10b2aa-ea99-4a41-b9e4-544fe94216d5.jpg":1,
  "e0e578de-26e4-48a8-ade7-25cdd2c01563.jpg":3,
  "ee270038-d0be-4f81-9fbd-67f17a66b30f.jpg":3,
  "f06a7a08-f80f-45d9-9d1b-e19f23cab034.jpg":3,
  "f54d8845-37df-4fd0-937b-b19344a51b46.jpg":4,
  "f720ac62-48c8-456c-8204-36b52fb04688.jpg":3,
  "f73d1116-cd9c-45bd-afed-7ab0a019cf2f.jpg":6,
  "ff08b75f-f00f-4490-9c72-0102cdf982a6.jpg":5, 
  "ffcd5e22-5740-45f4-bdc0-5b18d0f7c08d.jpg":2,
  
  
}

camera = CameraProcessor(0)
analyzer = camera.analyzer
camera.setup()

def check_parameter(min_value, max_value, step):
  best_result  = 0.0
  best_parameter = min_value
  for i in range(min_value, max_value, step):
    image_set = list(images)
    analyzer.check_parameter = i
    result = run_set(image_set)
    if(result > best_result): 
      best_parameter = i
      best_result = result
  return (best_result, best_parameter)
  
def run_set(images):
  score = 0
  while True:
    file, im = next_image(images)
  
    if (im==None):
      break
    camera.process_image(im)
    guess = camera.analyzer.points
    print("Guessed %d, answer %d" % (guess, answers[file]))
    if (guess == answers[file]): 
      score += 1
      cv2.waitKey(0)
    else:
      cv2.waitKey(0)
      pass
  
  result = float(score) / len(answers)
  print("Score: %f" % result)
  return result

#best_result, best_parameter = check_parameter(1,40,1)
#print("The best value is %d, result %f" % (best_parameter, best_result))
analyzer.check_parameter = 15
run_set(images)