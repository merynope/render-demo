// Define motor control pins
const int motorPin1 = 9; // IN1 on H-bridge
const int motorPin2 = 10; // IN2 on H-bridge
const int enablePin = 11; // Enable pin for motor speed control (PWM)

// Define timing intervals (milliseconds)
const unsigned long motorRunTime = 3000; // Time for the conveyor belt to run
const unsigned long motorStopTime = 2000; // Time for the conveyor belt to stop

// Variables to manage timing
unsigned long previousMillis = 0;
bool isMotorRunning = false;

void setup() {
  // Initialize motor control pins as outputs
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);

  // Start with the motor stopped
  stopMotor();
}

void loop() {
  unsigned long currentMillis = millis();

  if (isMotorRunning) {
    // Check if it's time to stop the motor
    if (currentMillis - previousMillis >= motorRunTime) {
      stopMotor();
      previousMillis = currentMillis; // Reset timer
    }
  } else {
    // Check if it's time to start the motor
    if (currentMillis - previousMillis >= motorStopTime) {
      startMotor();
      previousMillis = currentMillis; // Reset timer
    }
  }
}

void startMotor() {
  // Rotate the conveyor belt forward
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 150); // Set motor speed (0-255)
  isMotorRunning = true;
}

void stopMotor() {
  // Stop the conveyor belt
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  isMotorRunning = false;
}