/*
 The circuit:
 * LCD RS pin to digital pin 12/
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)
 * DHT output pin to digital pin 6
 * IR sensors output pin to digital pin 7 and 8
 */

#include <LiquidCrystal.h>
#include <dht.h>
dht DHT;
int temp_hum = 6;

int inRead = 8;
int outRead = 7;
String inp;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
int persons = 0;
int stk = 0;

void setup() {
  Serial.begin(9600);
  inp = "EHD PRoJECT!";
  lcd.begin(16,2);
  lcd.setCursor(0, 0);
  for (int i = 0; i < inp.length(); i++) {
    if(i==16)  lcd.setCursor(0,1);
    lcd.print(inp[i]);
  }
  
  pinMode(inRead, INPUT);
  pinMode(outRead, INPUT);
}

void loop() {
  int chk = DHT.read11(temp_hum);
  char ch[3];
  dtostrf(DHT.temperature, 2, 1, ch);
  String output = "0:"+String(ch);
  dtostrf(DHT.humidity, 2, 1, ch);
  output += "-1:"+String(ch);
  output += "-2:"+String(persons);
  Serial.println(output);
  
  int cnt = 0;
  while(cnt<10){
    recvInfo();
    
    int cnt2 = 0;
    while(cnt2 < 50){
      if(countPersons())  break;
      cnt2++;
    }
    
    cnt++;
  }
}

boolean countPersons(){
  int in = digitalRead(inRead);
  int out = digitalRead(outRead);
  
  if(in == HIGH){
    if(stk == 0 || stk == 1){
      stk = 1;
      delay(20)
      return false;
    }
    else if(stk == -1){
      stk = 0;
      persons--;
      delay(1000);
      return true;
    }
  }
  else if(out == HIGH){
    if(stk == 0 || stk == -1){
      stk = -1;
      delay(20)
      return false;
    }
    else if(stk == 1){
      stk = 0;
      persons++;
      delay(1000);
      return true;
    }
  }
  else{
    delay(20);
    return false;
  }
}

void recvInfo() {
  if (Serial.available() > 0) {
    inp = Serial.readString();
    
    lcd.clear();
    lcd.setCursor(0, 0);
    for (int i = 0; i < inp.length(); i++) {
      if(inp[i]!='~'){
        if(i==16)  lcd.setCursor(0,1);
        lcd.print(inp[i]);
      }
    }
  }
}

