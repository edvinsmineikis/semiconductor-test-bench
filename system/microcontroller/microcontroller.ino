#include <ArduinoJson.h>
#define PIN_HEATER 3
#define PIN_COOLER 4
#define TEMP_MUL 5.0 / 1024.0 * 1
#define PIN_HI_V_G 5
#define PIN_HI_V_DS 6
#define PIN_HI_V_G_EN 7
#define PIN_HI_V_DS_EN 8

bool tempController = false;
volatile float tempValue = 0;
float tempTarget = 25.0;
float coefP = 1.0;
float coefI = 1.0;
float I = 0;


void setup() {
  Serial.begin(9600);
  pinMode(PIN_HEATER, OUTPUT);
  pinMode(PIN_COOLER, OUTPUT);
  pinMode(PIN_HI_V_G, OUTPUT);
  pinMode(PIN_HI_V_DS, OUTPUT);
  pinMode(PIN_HI_V_G_EN, INPUT);
  pinMode(PIN_HI_V_DS_EN, INPUT);

  // Set up the timer to trigger every 10ms
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 156;  // 16MHz clock, prescaler of 1024, 156 = 10ms
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12) | (1 << CS10);  // prescaler of 1024
  TIMSK1 |= (1 << OCIE1A);
}

ISR(TIMER1_COMPA_vect) {
  if (tempController == true) {
    tempValue = analogRead(A0) * TEMP_MUL;
    updateController();
  }
}

void updateController() {
  float P = (tempTarget - tempValue) * coefP;
  I += (tempTarget - tempValue) * coefI;

  if (P + I > 0.0) {
    digitalWrite(PIN_COOLER, LOW);
    digitalWrite(PIN_HEATER, HIGH);
  } else {
    digitalWrite(PIN_COOLER, HIGH);
    digitalWrite(PIN_HEATER, LOW);
  }
}

void loop() {
  // Communication handling
  if (Serial.available()) {
    StaticJsonDocument<128> dataIn;
    StaticJsonDocument<128> dataOut;

    DeserializationError err = deserializeJson(dataIn, Serial.readStringUntil('\n'));
    if (err) {
      dataOut["status"] = 1;  // Deserialization error
    } else {
      if (dataIn.containsKey("cmd")) {
        dataOut["status"] = 0;
        if (dataIn["cmd"].as<String>() == "getTemp") {
          dataOut["temp"] = tempValue;
        }
        if (dataIn["cmd"].as<String>() == "getTempTarget") {
          dataOut["tempTarget"] = tempTarget;
        }
        if (dataIn["cmd"].as<String>() == "getCoefP") {
          dataOut["coefP"] = coefP;
        }
        if (dataIn["cmd"].as<String>() == "getCoefI") {
          dataOut["coefI"] = coefI;
        }
        if (dataIn["cmd"].as<String>() == "enableTempController") {
          tempController = true;
        }
        if (dataIn["cmd"].as<String>() == "disableTempController") {
          tempController = false;
          digitalWrite(PIN_HEATER, LOW);
          digitalWrite(PIN_COOLER, LOW);
        }
        if (dataIn["cmd"].as<String>() == "setTempTarget") {
          tempTarget = (float)dataIn["tempTarget"];
        }
        if (dataIn["cmd"].as<String>() == "setCoefP") {
          coefP = (float)dataIn["coefP"];
        }
        if (dataIn["cmd"].as<String>() == "setCoefI") {
          coefI = (float)dataIn["coefI"];
        }
      } else {
        dataOut["status"] = 2;  // No "cmd" key
      }
    }
    serializeJson(dataOut, Serial);
    Serial.write('\n');
  }

  // Relay safety, HiVG and HiVDS cannot be on at same time
  if (digitalRead(PIN_HI_V_G_EN) && !digitalRead(PIN_HI_V_DS)) {
    digitalWrite(PIN_HI_V_G, HIGH);
  }
  else {
    digitalWrite(PIN_HI_V_G, LOW);
  }

  if (digitalRead(PIN_HI_V_DS_EN) && !digitalRead(PIN_HI_V_G)) {
    digitalWrite(PIN_HI_V_DS, HIGH);
  }
  else {
    digitalWrite(PIN_HI_V_DS, LOW);
  }
}
