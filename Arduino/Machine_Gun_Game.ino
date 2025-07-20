#include <Servo.h>
#include <AccelStepper.h>

Servo loadServo; 
const int loadServoPin = 7; 

int loadCurrentServoPos = 180; 
int loadTargetServoPos = 180; 
long loadLastServoMoveTime = 0; 
int loadServoMoveInterval = 15;
bool loadServoMoving = false; 
int loadMoveStep = 1; 


enum LoadState {IDLE, MOVING_DOWN, WAITING_MIDDLE, MOVING_UP };
LoadState currentLoadState = IDLE; 
long loadLastStateChangeTime = 0;
long loadMiddleWaitTime = 1000; 


bool loadProcessedSinceLastFire = false; 
long loadServoStartTime = 0; 
const long loadCompleteDelay = 7000; 

// --- Stepper Motor Variables ---
AccelStepper stepper(AccelStepper::FULL4WIRE, 8, 10, 9, 11);

const float stepsPerDegree = 2048.0 / 360.0; 
long stepperTargetSteps; 

// --- Fire Servo Variables ---
Servo fireServo; 
const int fireServoPin = 6;

int fireCurrentServoAngle = 130;
int fireTargetServoAngle=65;
bool fireServoMoving = false; 
unsigned long firePreviousServoMillis = 0; 
const long fireServoInterval = 5; 
void setup() {
  Serial.begin(9600); 

 
  loadServo.attach(loadServoPin);
  loadServo.write(loadCurrentServoPos);


  fireServo.attach(fireServoPin);
  fireServo.write(fireCurrentServoAngle);

  
  stepper.setMaxSpeed(400); 
  stepper.setAcceleration(200);
  stepper.setCurrentPosition(0);
}

void loop() {
  unsigned long currentTime = millis(); 

 
  if (Serial.available()) { 
    String incoming = Serial.readStringUntil('\n'); 
    incoming.trim(); 

    // Check if the incoming string is a numeric value (for stepper control)
    bool isNumeric = true;
    for (int i = 0; i < incoming.length(); i++) {
      // Allow numbers, negative sign, and decimal point for negative angles/floating point values
      if (!isDigit(incoming.charAt(i)) && incoming.charAt(i) != '-' && incoming.charAt(i) != '.') {
        isNumeric = false;
        break;
      }
    }

    if (isNumeric) {
      int angle = incoming.toInt();
      stepperTargetSteps = (long)(angle * stepsPerDegree);
      stepper.moveTo(stepperTargetSteps); // Set the stepper motor's target position
    }
    // Check for "Load" command
    else if (incoming == "Load") {
      if (currentLoadState == IDLE && !loadProcessedSinceLastFire) { 
        loadTargetServoPos = 35;
        loadServoMoving = true;
        loadMoveStep = -1;
        currentLoadState = MOVING_DOWN;
        loadLastServoMoveTime = currentTime;
        loadProcessedSinceLastFire = true;
        loadServoStartTime = currentTime; 
      }
    }
    // Check for "FIRE" command
    else if (incoming == "FIRE") {
      if (loadProcessedSinceLastFire && !fireServoMoving && (currentTime - loadServoStartTime >= loadCompleteDelay)) { 
        fireCurrentServoAngle = fireServo.read(); 
        fireTargetServoAngle =65; 
        fireServoMoving = true; 
      }
    }
  }

  // --- Load Servo Movement Control ---
  if (loadServoMoving) { 
    if (currentTime - loadLastServoMoveTime >= loadServoMoveInterval) { // Check if enough time has passed for a micro-step
      loadLastServoMoveTime = currentTime; // Update the last move time
      loadCurrentServoPos += loadMoveStep; // Move the servo by one step

      // Check if the servo has reached its target position
      if ((loadMoveStep == 1 && loadCurrentServoPos >= loadTargetServoPos) ||
          (loadMoveStep == -1 && loadCurrentServoPos <= loadTargetServoPos)) {
        loadCurrentServoPos = loadTargetServoPos; // Ensure it settles exactly at the target
        loadServoMoving = false; // Stop the movement

        // State transitions for the loading mechanism
        if (currentLoadState == MOVING_DOWN) {
          currentLoadState = WAITING_MIDDLE; // Transition to waiting state after moving down
          loadLastStateChangeTime = currentTime; // Record the time of this state change
        } else if (currentLoadState == MOVING_UP) {
          currentLoadState = IDLE; // Transition to IDLE after moving up, indicating completion
          loadServoMoving = false; // Ensure servo stops moving
        }
      }
      loadServo.write(loadCurrentServoPos); // Write the new position to the servo
    }
  }

  // --- Load Servo Waiting State ---
  if (currentLoadState == WAITING_MIDDLE) { // If in the waiting state
    if (currentTime - loadLastStateChangeTime >= loadMiddleWaitTime) { // Check if the wait time has elapsed
      loadTargetServoPos = 250; // Set target to move the servo back up
      loadServoMoving = true; // Start movement
      loadMoveStep = 1; // Set direction to increase angle
      currentLoadState = MOVING_UP; // Change state to MOVING_UP
      loadLastServoMoveTime = currentTime; // Record the time of this state change
    }
  }

  // --- Fire Servo Movement Control ---
  if (fireServoMoving) { // If the fire servo is currently set to move
    if (currentTime - firePreviousServoMillis >= fireServoInterval) { // Check if enough time has passed for a micro-step
      firePreviousServoMillis = currentTime; // Update the last move time

      // Move the servo towards the target angle
      if (fireCurrentServoAngle < fireTargetServoAngle) {
        fireCurrentServoAngle++; // Increment angle if less than target
        fireServo.write(fireCurrentServoAngle);
      } else if (fireCurrentServoAngle > fireTargetServoAngle) {
        fireCurrentServoAngle--; // Decrement angle if greater than target
        fireServo.write(fireCurrentServoAngle);
      }

      // Check if the fire servo has reached its target angle
      if (fireCurrentServoAngle == fireTargetServoAngle) {
        if (fireTargetServoAngle == 65) { // If it reached the firing position
          fireTargetServoAngle = 130; // Set the target back to the initial (resting) position (this was changed by you)
        }
      
        else if (fireTargetServoAngle == 130) { // If it reached the resting position 
          fireServoMoving = false; // Stop the fire servo movement
          // Reset stepper position to 0 after firing
          stepper.moveTo(abs(stepperTargetSteps) - abs(stepperTargetSteps)); // This effectively sets target to 0
          loadProcessedSinceLastFire = false; // Reset the 'Load' flag to allow a new 'Load' command
          loadServoStartTime = 0; // Reset the load start time after fire cycle completes
        }
      }
    }
  }

  // --- Stepper Motor Control ---
  stepper.run(); // Run the stepper motor
}
