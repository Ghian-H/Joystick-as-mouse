const int X_PIN = A0;
const int Y_PIN = A1;
const int SW_PIN = 2;

void setup() {
  Serial.begin(9600);
  pinMode(SW_PIN, INPUT_PULLUP);
}

void loop() {
  int xVal = analogRead(X_PIN);
  int yVal = analogRead(Y_PIN);
  int swVal = digitalRead(SW_PIN); // 0 = pressed, 1 = released

  Serial.print(xVal);
  Serial.print(",");
  Serial.print(yVal);
  Serial.print(",");
  Serial.println(swVal);

  delay(10);
}