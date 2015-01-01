/*
 *  These are pairs of numbers, the first is the
 *  time to turn the LED on, the second is the 
 *  time to turn the LED off
 */
unsigned int raw_times[] = {
    710,
    960,
    2410,
    3360
};

unsigned char raw_10s[] = {
    3, 3,
    1, 2,
    1, 2,
    1, 0,
    1, 2,
    1, 2,
    1, 2,
    1, 0,
    1, 2,
    1, 2,
    1, 2,
    1, 0,
    1, 0,
    1, 0,
    1, 2,
    1, 0,
    1, 0,
    1, 0,
    1, 2,
    1, 0,
    1, 0
};

const unsigned int LED = 13;


// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin 13 as an output.
  pinMode(LED, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  int n10s = sizeof raw_10s;
  
  for (int i = 0; i < n10s; i += 2) {
      digitalWrite(LED, HIGH);
      delayMicroseconds(raw_times[raw_10s[i]] * 10);
      
      digitalWrite(LED, LOW);
      delayMicroseconds(raw_times[raw_10s[i + 1]] * 10);
  }
  
  delay(2000);
}
