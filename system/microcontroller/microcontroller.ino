#include <ArduinoJson.h>
#define PIN_HEATER 5
#define PIN_COOLER 4
#define PIN_HI_V_G 2
#define PIN_HI_V_DS 3
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
float coefP = 2.0;
float coefI = 0.1;
float I = 0;

void setup() {
  Serial.begin(57600);
  pinMode(PIN_HEATER, OUTPUT);
  pinMode(PIN_COOLER, OUTPUT);
  pinMode(PIN_HI_V_G, OUTPUT);
  pinMode(PIN_HI_V_DS, OUTPUT);
  pinMode(PIN_HI_V_G_RELAY, OUTPUT);
  pinMode(PIN_PWM_RELAY, OUTPUT);
  pinMode(PIN_PWM, OUTPUT);

  // Ultra fast PWM
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1A |= (1 << WGM11);
  TCCR1B |= (1 << WGM13) | (1 << WGM12);
  TCCR1A |= (1 << COM1A1);
  //ICR1 = 799; // 10kHz
  ICR1 = 7999; // 1kHz
  OCR1A = ICR1 / 2;
  TCCR1B |= (1 << CS10);

  // Set up the timer to trigger every 10ms
  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 0;
  OCR2A = 156;
  TCCR2B |= (1 << WGM12);
  TCCR2B |= (1 << CS22) | (1 << CS21) | (1 << CS20);
  TIMSK2 |= (1 << OCIE2A);
}

ISR(TIMER2_COMPA_vect) {
  tempValue = analogRead(PIN_TEMP) * TEMP_MUL;
  if (tempController == true) {
    updateController();
  }
}


void updateController() {
  float error = (tempTarget - tempValue);
  float P = error * coefP;
  if (error > 0) {
    if (P + I < 255) {
      I += error * coefI;
    }
    else {
      I = 254;
    }
  }
  if (error < 0) {
    if (P + I > 0) {
      I += error * coefI;
    }
    else {
      I = 1;
    }
  }

  analogWrite(PIN_HEATER, constrain(P + I, 0, 255));
  digitalWrite(PIN_COOLER, P < -1.0);
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
        else if (dataIn["cmd"].as<String>() == "enableFan") {
          digitalWrite(PIN_COOLER, HIGH);
        }
        else if (dataIn["cmd"].as<String>() == "disableFan") {
          digitalWrite(PIN_COOLER, LOW);
        }
        else if (dataIn["cmd"].as<String>() == "enableTempController") {
          tempController = true;
        }
        else if (dataIn["cmd"].as<String>() == "disableTempController") {
          tempController = false;
          analogWrite(PIN_HEATER, 0);
          digitalWrite(PIN_COOLER, LOW);
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
        else if (dataIn["cmd"].as<String>() == "setPwmFreq") {
          long icr1_value = (F_CPU / (2 * 1 * (int)dataIn["value"])) - 1;
          ICR1 = icr1_value;
          OCR1A = ICR1 / 2;
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
        else if (dataIn["cmd"].as<String>() == "enablePwmRelay") {
          if (!digitalRead(PIN_HI_V_G_RELAY)) {
            digitalWrite(PIN_PWM_RELAY, HIGH);
          }
          else {
            dataOut["status"] = 4;
          }
        }
        else if (dataIn["cmd"].as<String>() == "disablePwmRelay") {
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
