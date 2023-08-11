#include <ArduinoJson.h>
#define PIN_HEATER 3
#define PIN_COOLER 4
#define PIN_HI_V_G 5
#define PIN_HI_V_DS 6
#define PIN_HI_V_G_RELAY 7
#define PIN_PWM_RELAY 8
#define PIN_PWM 9
#define PIN_TEMP A0

/*
  T1 = 16
  V1 = 0.538902148
  T2 = 180
  V2 = 2.842521167
  y = ax + b
  a = (T2-T1)/(V2-V1) = 71.19232766
  b = -a*V1+T1 = -22.3656982971
*/
#define TEMP_MUL 5.0/1024.0*71.19232766-22.3656982971

bool tempController = false;
volatile float tempValue = 0;
float tempTarget = 25.0;
float coefP = 1.0;
float coefI = 1.0;
float coefD = 1.0;
float I = 0;
float D = 0;


void setup() {
  Serial.begin(57600);
  pinMode(PIN_HEATER, OUTPUT);
  pinMode(PIN_COOLER, OUTPUT);
  pinMode(PIN_HI_V_G, OUTPUT);
  pinMode(PIN_HI_V_DS, OUTPUT);
  pinMode(PIN_HI_V_G_RELAY, OUTPUT);
  pinMode(PIN_PWM_RELAY, OUTPUT);
  pinMode(PIN_PWM, OUTPUT);

  // Set up the timer to trigger every 10ms
  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 0;
  OCR2A = 156;  // 16MHz clock, prescaler of 1024, 156 = 10ms
  TCCR2B |= (1 << WGM12);
  TCCR2B |= (1 << CS22) | (1 << CS21) | (1 << CS20);  // prescaler of 1024
  TIMSK2 |= (1 << OCIE2A);
}

ISR(TIMER2_COMPA_vect) {
  tempValue = analogRead(PIN_TEMP) * TEMP_MUL;
  if (tempController == true) {
    updateController();
  }
}


void updateController() {
  float P = (tempTarget - tempValue) * coefP;
  I += (tempTarget - tempValue) * coefI;
  D = (tempValue - D) * coefD;
  

  if (P + I + D > 0.0) {
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
    StaticJsonDocument<64> dataIn;
    StaticJsonDocument<64> dataOut;

    DeserializationError err = deserializeJson(dataIn, Serial.readStringUntil('\n'));
    if (err) {
      dataOut["status"] = 1;  // Deserialization error
    } else {
      if (dataIn.containsKey("cmd")) {
        dataOut["status"] = 0;
        if (dataIn["cmd"].as<String>() == "getTemp") {
          dataOut["temp"] = tempValue;
        }
        else if (dataIn["cmd"].as<String>() == "getTempTarget") {
          dataOut["tempTarget"] = tempTarget;
        }
        else if (dataIn["cmd"].as<String>() == "getCoefP") {
          dataOut["coefP"] = coefP;
        }
        else if (dataIn["cmd"].as<String>() == "getCoefI") {
          dataOut["coefI"] = coefI;
        }
        else if (dataIn["cmd"].as<String>() == "getCoefD") {
          dataOut["coefD"] = coefD;
        }
        else if (dataIn["cmd"].as<String>() == "enableTempController") {
          tempController = true;
        }
        else if (dataIn["cmd"].as<String>() == "disableTempController") {
          tempController = false;
          digitalWrite(PIN_HEATER, LOW);
          digitalWrite(PIN_COOLER, LOW);
        }
        else if (dataIn["cmd"].as<String>() == "resetTempController") {
          I = 0;
        }
        else if (dataIn["cmd"].as<String>() == "setTempTarget") {
          tempTarget = (float)dataIn["value"];
        }
        else if (dataIn["cmd"].as<String>() == "setCoefP") {
          coefP = (float)dataIn["value"];
        }
        else if (dataIn["cmd"].as<String>() == "setCoefI") {
          coefI = (float)dataIn["value"];
        }
        else if (dataIn["cmd"].as<String>() == "setCoefD") {
          coefD = (float)dataIn["value"];
        }
        else if (dataIn["cmd"].as<String>() == "enableHiVg") {
          digitalWrite(PIN_HI_V_G, HIGH);
        }
        else if (dataIn["cmd"].as<String>() == "disableHiVg") {
          digitalWrite(PIN_HI_V_G, LOW);
        }
        else if (dataIn["cmd"].as<String>() == "enableHiVds") {
          digitalWrite(PIN_HI_V_DS, HIGH);
        }
        else if (dataIn["cmd"].as<String>() == "disableHiVds") {
          digitalWrite(PIN_HI_V_DS, LOW);
        }
        else if (dataIn["cmd"].as<String>() == "enableHiVgRelay") {
          if (!digitalRead(PIN_PWM_RELAY)) {
            digitalWrite(PIN_HI_V_G_RELAY, HIGH);
          }
          else {
            dataOut["status"] = 4;
          }
        }
        else if (dataIn["cmd"].as<String>() == "disableHiVgRelay") {
          digitalWrite(PIN_HI_V_G_RELAY, LOW);
        }
        else if (dataIn["cmd"].as<String>() == "setPwm") {
          analogWrite(PIN_PWM, dataIn["value"]);
        }
        else if (dataIn["cmd"].as<String>() == "setPwmRelayOn") {
          if (!digitalRead(PIN_HI_V_G_RELAY)) {
            digitalWrite(PIN_PWM_RELAY, HIGH);
          }
          else {
            dataOut["status"] = 4;
          }
        }
        else if (dataIn["cmd"].as<String>() == "setPwmRelayOff") {
          digitalWrite(PIN_PWM_RELAY, LOW);
        }
        else {
          dataOut["status"] = 3;
        }
      } else {
        dataOut["status"] = 2;  // No "cmd" key
      }
    }
    serializeJson(dataOut, Serial);
    Serial.write('\n');
  }
}
