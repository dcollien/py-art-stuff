#include <Servo.h>

Servo servo;

// awaiting command
String command  = "";
String argument = "";

int servoMin = 19;
int servoMax = 162;

void setup() {
  servo.attach(9);    // Servo data pin is on Pin 9
  Serial.begin(9600); // Listen for serial commands with baud 9600
}

void loop() {
  int pos;
  
  if (command == "servo") {
    Serial.print("Turning to angle: ");
    Serial.println(argument);
    pos = argument.toFloat() * (servoMax - servoMin);
    pos = pos % (servoMax - servoMin + 1);
    pos += servoMin;
    servo.write(pos);
    command = "";
  }
}

void serialEvent() {
  while (Serial.available()) {
    command = Serial.readStringUntil(' ');
    argument = Serial.readStringUntil('\n');
  }
}

