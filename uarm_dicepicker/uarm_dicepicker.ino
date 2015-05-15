/************************************************************************
* File Name          : position test
* Author             : Richard
* Version            : V0.0.1
* Date               : 13 May, 2015
* Description        : uArm positioning
* License            : 
* Copyright(C) 2015 Richard.
*************************************************************************/

#include <EEPROM.h>
#include <UF_uArm.h>
int pickupAngle;
int pickupStretch;
int waitingForPickup;
bool interactiveMode;

int angle;
int stretch;
int height;
int hand_angle;

UF_uArm uarm;           // initialize the uArm library 
void setup() 
{
  uarm.init();          // initialize the uArm position
  Serial.begin(9600);  // start serial port at 9600 bps
  detachServo();
  Serial.println("Hello! Please enter one of the following:");
  Serial.println("c for callibration");
  Serial.println("p for pickup");
  Serial.println("r for report");
  Serial.println("g for gripper test");
  Serial.println("i for interactive mode");
  setSpeeds();
  safeState();
  
}

void safeState(){
  
  angle = 0;
  stretch = 20;
  height = 93;
  hand_angle = -20;
  setPosition();
}

void setPosition() {
  uarm.setPosition(stretch, height, angle, hand_angle);
}

void loop()
{
  while(Serial.available() > 0) {
    int command = Serial.read();
    if(interactiveMode) { 
      handleInteractive(command);
    }else if(waitingForPickup != 0) {
      handlePickupState(command);
    }else{
      if (command == 99) doCallibration();
      if (command == 112) waitingForPickup = 1; 
      if (command == 114) printState();
      if (command == 103) doGripperTest();
      if (command == 105) {
        safeState();
        interactiveMode = true;
        Serial.println("Ok, enter commands. Press o to exit interactive mode.");
      }
    }
  }
} 

void handleInteractive(int command) {
  if (command == 97) angle -= 1;
  if (command == 100) angle += 1; 
  if (command == 101) height -= 5;
  if (command == 113) height += 5;
  if (command == 119) stretch += 5;
  if (command == 115) stretch -= 5;
  if (command == 111) {
    interactiveMode = false;  
    safeState();
  }
  setPosition();
  printPosition();
}

void handlePickupState(int command) {
  if(waitingForPickup == 1) {
    // take only the first 4 bits so that we can use ascii @ for value 0
    pickupAngle = command & 63;
    waitingForPickup = 2; 
  }else if(waitingForPickup == 2) {
    pickupStretch = command;
    doPickup(pickupAngle, pickupStretch);
    waitingForPickup = 0;
  }
}

void doGripperTest(){
  Serial.println("I give you, the gripper test!");
  uarm.gripperCatch();
    printState();
  Serial.println("Voila! Closed!"); 
  delay(2000);
  uarm.gripperRelease();  
  Serial.println("Thankyoubyebye!");
}

void doPickup(int angle, int stretch) {
  uarm.gripperRelease();
  Serial.println("Going to position");
  uarm.setPosition(20, 92, 0, 0);
  delay(500);
  uarm.setPosition(stretch, 92, 0, 0);
  delay(1000);
  uarm.setPosition(stretch, 30, angle, 0);
  delay(2000);
  Serial.println("Moving down");
  uarm.setPosition(stretch, 7, angle, 0);
  delay(500);
  Serial.println("Closing gripper");
  uarm.gripperCatch();
  delay(500);
  Serial.println("Backing out");
  uarm.setPosition(stretch, 92, angle, 0);
  delay(500);
  Serial.println("Moving to the slide for dropoff");
  uarm.setPosition(100, 180, -45, 0);
  delay(2000);
  Serial.println("And... release!");
  uarm.gripperRelease();
  delay(500);
  Serial.println("Moving back");
  uarm.setPosition(80, 180, 0, 0);
  delay(2000);
  safeState();
}

void doCallibration() {
  Serial.println("Please place the dice");
  uarm.gripperCatch();
  delay(400);
  Serial.println("Going to middle of the field");
  uarm.setPosition(80, 180, 0, -20);
  delay(1000);
  uarm.setPosition(80, 10, 0, -20);
  delay(1800);
  Serial.println("Releasing dice");
  uarm.gripperRelease();
  delay(200);
  Serial.println("Pulling back");
  delay(200);
  safeState();
}

void printPosition() {
  Serial.print(stretch);
  Serial.print(",");
  Serial.print(height);
  Serial.print(",");
  Serial.print(angle);
  Serial.print(",");  
  Serial.print(hand_angle);
  Serial.print("\n");
}

void printState() {
  int l_angle = uarm.readMappedAngle(SERVO_L);
  int r_angle = uarm.readMappedAngle(SERVO_R);
  int rot_angle = uarm.readMappedAngle(SERVO_ROT);
  int hand_rot_angle = uarm.readMappedAngle(SERVO_HAND_ROT);
  int hand_angle = uarm.readMappedAngle(SERVO_HAND);
  Serial.print(l_angle);
  Serial.print(",");
  Serial.print(r_angle);
  Serial.print(",");
  Serial.print(rot_angle);
  Serial.print(",");  
  Serial.print(hand_rot_angle);
  Serial.print(",");
  Serial.print(hand_angle);
  Serial.print("\r\n");
}


void detachServo()
{
  //uarm.detachServo(SERVO_L);
  //uarm.detachServo(SERVO_R);
  //uarm.detachServo(SERVO_ROT);
  //uarm.detachServo(SERVO_HAND_ROT);
  //uarm.detachServo(SERVO_HAND);
}

void setSpeeds() {
   uarm.setServoSpeed(SERVO_L, 20);
   uarm.setServoSpeed(SERVO_R, 20);
   uarm.setServoSpeed(SERVO_ROT, 20);
   uarm.setServoSpeed(SERVO_HAND_ROT, 100);
   uarm.setServoSpeed(SERVO_HAND, 200);
   
}
