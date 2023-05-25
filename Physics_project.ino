#include <Keypad.h>
#include <SPI.h>
#include <Arduino.h>

const byte ROWS = 4; 
const byte COLS = 4; 

char hexaKeys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6}; 
byte colPins[COLS] = {5, 4, 3, 2}; 

Keypad customKeypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS); 

const int NUM_SWITCHES = 12;
bool switches[NUM_SWITCHES];

// Array for python
const int MAX_ELEMENTS = 20;
int table[MAX_ELEMENTS];
int waiter[MAX_ELEMENTS];
int table_size = 0;
int waiter_size = 0;

int count = 0;

// Pin definitions
const int SER_Pin = 11;     // Connect to SER pin of the first shift register
const int SRCLK_Pin = 12;   // Connect to SRCLK pin of all shift registers
const int RCLK_Pin = 13;    // Connect to RCLK pin of all shift registers

// Number of shift registers
const int numRegisters = 8;

// LED state array
bool ledState[64];

// Function to update the shift registers
void updateRegisters(){
  digitalWrite(RCLK_Pin, LOW);
  
  // Loop through each shift register
  for (int i = numRegisters - 1; i >= 0; i--)
  {
    // Initialize a byte to store the state of all 8 LEDs in the current register
    byte currentState = 0;
    
    // Loop through each LED controlled by the current shift register
    for (int j = 0; j < 8; j++)
    {
      // Set the appropriate bit in currentState based on the state of the current LED
      bitWrite(currentState, j, ledState[i * 8 + j]);
    }
    
    // Shift out the state of all 8 LEDs in the current register at once
    shiftOut(SER_Pin, SRCLK_Pin, MSBFIRST, currentState);
  }
  
  digitalWrite(RCLK_Pin, HIGH);
}

// Function to turn on/off an LED
void led(int ledIndex, bool state){
  if (ledIndex >= 1 && ledIndex <= 64)
  {
    ledState[ledIndex - 1] = state;
    updateRegisters();
  }
}

void turnOnAllLEDs() {
  for (int i = 1; i <= 64; i++) {
    led(i, true);
  }
}

void turnOffAllLEDs() {
  for (int i = 1; i <= 64; i++) {
    led(i, false);
  }
}

void setup(){
  Serial.begin(9600);
  pinMode(SER_Pin, OUTPUT);
  pinMode(SRCLK_Pin, OUTPUT);
  pinMode(RCLK_Pin, OUTPUT);
  
  // Set all LEDs initially off
  for (int i = 0; i < 64; i++)
  {
    ledState[i] = false;
  }
  
  updateRegisters();  // Initialize the shift registers

}
  
void loop(){
  char customKey = customKeypad.getKey();
  int index;
  // Gives number pressed an index
  switch (customKey) {
    case '1':
      index = 0;
      break;
    case '2':
      index = 1;
      break;
    case '3':
      index = 2;
      break;
    case '4':
      index = 3;
      break;
    case '5':
      index = 4;
      break;
    case '6':
      index = 5;
      break;
    case '7':
      index = 6;
      break;
    case '8':
      index = 7;
      break;
    case '9':
      index = 8;
      break;
    case '*':   
      index = 9;
      break;
    case '0':   
      index = 10;
      break;
    case '#':   
      index = 11;
      break;
    case 'A':
      index = 13;
      break;
    case 'D':
      index = 12;
      break;
    default:
      index = -1;
      break;
  }
  
  // Check if button 'A' is pressed and increases the count
  if (index == 12) {
    turnOnAllLEDs();
    delay(1000); // Wait for 1 second
    turnOffAllLEDs();
    count = count + 1;
    // if count is 1 then it shows the random tables and lets user play the game
    if (count == 1){
      showTable();
      user();
    }
    // if count is 2 then it shows the solution and resets
    else if (count == 2){
      turnOffAllLEDs();
      showTable();
      showWaiter();
      count = 0;
    }
  } 

  // Changes value of number pressed from 'true' to 'false' 
  if (index >= 0 && index < NUM_SWITCHES && count == 1) {
    switches[index] = !switches[index];
    user();
  }

  // Reads data in serial and runs function that proccesses it
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    parseData(data);
  }
}

// Seperates data from python file and runs funciton that gets the size 
void parseData(String data) {
  int separatorIndex = data.indexOf('|');
  String table_data = data.substring(0, separatorIndex);
  String waiter_data = data.substring(separatorIndex + 1);

  
  table_size = parseArray(table_data, table, MAX_ELEMENTS);
  waiter_size = parseArray(waiter_data, waiter, MAX_ELEMENTS);
  turnOnAllLEDs();
  delay(1000); // Wait for 1 second
  turnOffAllLEDs();
}

// Gets size of array
int parseArray(String data, int* array, int max_size) {
  int size = 0;
  int start = 0;
  int end = data.indexOf(',');
  
  if (data.length() == 0) {
    Serial.println("Error: Input string is empty");
    return size;
  }

  while (end != -1 && size < max_size) {
    String strValue = data.substring(start, end);
    if (isNumeric(strValue)) {
      array[size++] = strValue.toInt();
    } else {
      Serial.println("Error: Non-numeric value encountered");
    }
    start = end + 1;
    end = data.indexOf(',', start);
  }
  
  if (size < max_size) {
    String strValue = data.substring(start);
    if (isNumeric(strValue)) {
      array[size++] = strValue.toInt();
    } else {
      Serial.println("Error: Non-numeric value encountered");
    }
  }
  
  return size;
}

boolean isNumeric(String str) {
  for (byte i = 0; i < str.length(); i++) {
    if (!isDigit(str.charAt(i))) {
      return false;
    }
  }
  return true;
}

// Turns the LED's for the tables
void showTable() {
  for (int i = 0; i < table_size; i++) {
    if (table[i] == 1){
      led(1,true); 
      led(2,true);
    }
    else if (table[i] == 2){
      led(3,true); 
      led(4,true);
    }
    else if (table[i] == 3){
      led(5,true); 
      led(6,true);
    }
    else if (table[i] == 4){
      led(7,true);
      led(8,true); 
    }
    else if (table[i] == 5){
      led(9,true);
      led(10,true);
    }
    else if (table[i] == 6){
      led(11,true);
      led(12,true); 
    }
    else if (table[i] == 7){
      led(13,true);
      led(14,true);
    }
    else if (table[i] == 8){
      led(15,true);
      led(16,true);
    }
    else if (table[i] == 9){
      led(25,true);
      led(26,true);
    }
    else if (table[i] == 10){
      led(27,true);
      led(28,true);
    }
    else if (table[i] == 11){
      led(29,true);
      led(30,true);
    }
    else if (table[i] == 12){
      led(31,true);
      led(32,true);
    }
    else if (table[i] == 13){
      led(41,true);
      led(42,true);
    }
    else if (table[i] == 14){
      led(43,true);
      led(44,true);
    }
    else if (table[i] == 15){
      led(45,true);
      led(46,true);
    }
    else if (table[i] == 16){
      led(47,true);
      led(48,true);
    }
    else if (table[i] == 17){
      led(57,true);
      led(58,true);
    }
    else if (table[i] == 18){
      led(59,true);
      led(60,true);
    }
    else if (table[i] == 19){
      led(61,true);
      led(62,true);
    }
    else if (table[i] == 20){
      led(63,true);
      led(64,true);
    }
    else{
      //error
    }
  }
}

// Turns the LED's for the waiters (delays 0.5 second)
void showWaiter() {
  for (int i = 0; i < waiter_size; i++) {
    if (waiter[i] == 1){
      led(18,true);
      led(19,true);
    }
    else if (waiter[i] == 2){
      led(20,true);
      led(21,true);
    }
    else if (waiter[i] == 3){
      led(22,true);
      led(23,true);
    }
    else if (waiter[i] == 4){
      led(24,true);
      led(33,true);
    }
    else if (waiter[i] == 5){
      led(34,true);
      led(35,true);
    }
    else if (waiter[i] == 6){
      led(36,true);
      led(37,true);
    }
    else if (waiter[i] == 7){
      led(38,true);
      led(39,true);
    }
    else if (waiter[i] == 8){
      led(40,true);
      led(56,true);
    }
    else if (waiter[i] == 9){
      led(55,true);
      led(54,true);
    }
    else if (waiter[i] == 10){
      led(53,true);
      led(52,true);
    }
    else if (waiter[i] == 11){
      led(51,true);
      led(50,true);
    }
    else if (waiter[i] == 12){
      led(49,true);
      led(17,true);
    }
    delay(500);
  }
}

// Turns the LED's for the waiters from user input 
void user() {
  for (int index = 0; index < NUM_SWITCHES; index++) {
    bool true_false = switches[index];
    if (index == 0){
      led(18,true_false);
      led(19,true_false);
    }
    else if (index == 1){
      led(20,true_false);
      led(21,true_false);
    }
    else if (index == 2){
      led(22,true_false);
      led(23,true_false);
    }
    else if (index == 3){
      led(24,true_false);
      led(33,true_false);
    }
    else if (index == 4){
      led(34,true_false);
      led(35,true_false);
    }
    else if (index == 5){
      led(36,true_false);
      led(37,true_false);
    }
    else if (index == 6){
      led(38,true_false);
      led(39,true_false);
    }
    else if (index == 7){
      led(40,true_false);
      led(56,true_false);
    }
    else if (index == 8){
      led(55,true_false);
      led(54,true_false);
    }
    else if (index == 9){
      led(53,true_false);
      led(52,true_false);
    }
    else if (index == 10){
      led(51,true_false);
      led(50,true_false);
    }
    else if (index == 11){
      led(49,true_false);
      led(17,true_false);
    }
  }
}


