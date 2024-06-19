#include <CytronMotorDriver.h>

CytronMD motor_DepanKiri(PWM_DIR, 9, 8);  // PWM 1 = Pin 3, DIR 1 = Pin 4.
CytronMD motor_DepanKanan(PWM_DIR, 3, 2); // PWM 2 = Pin 9, DIR 2 = Pin 10.
CytronMD motor_BelakangKiri(PWM_DIR, 10, 12);
CytronMD motor_BelakangKanan(PWM_DIR, 11, 13);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n');
    receivedData.trim();  // Hapus karakter newline
    if (receivedData == "maju") {
      Serial.println("Mobil Maju");
      maju();
      delay(500);
    } else if (receivedData == "mundur"){
      Serial.println("Mobil Mundur");
      mundur();
      delay(1000);
    } else if (receivedData == "kiri"){
      Serial.println("Mobil Belok Kiri");
      kiri();
      delay(500);
    } else if (receivedData == "kanan"){
      Serial.println("Mobil Belok Kanan");
      kanan();
      delay(500);
    } else if (receivedData == "berhenti"){
      Serial.println("Mobil Berhenti");
      berhenti();
      delay(1000);
    }
  } else {
    // Ganti dengan Code untuk intput baterai, jika ada
    Serial.println("Arduino Stand by");
    delay(100);
  }
}

void maju() {
  motor_DepanKiri.setSpeed(255);  // Motor 1 runs backward at full speed.
  motor_DepanKanan.setSpeed(255);   // Motor 2 runs forward at full speed.
  motor_BelakangKiri.setSpeed(255);  // Motor 1 runs backward at full speed.
  motor_BelakangKanan.setSpeed(255);   // Motor 2 runs forward at full speed.
}

void berhenti(){
  motor_DepanKiri.setSpeed(0);  // Motor 1 runs backward at full speed.
  motor_DepanKanan.setSpeed(0);   // Motor 2 runs forward at full speed.
  motor_BelakangKiri.setSpeed(0);  // Motor 1 runs backward at full speed.
  motor_BelakangKanan.setSpeed(0);   // Motor 2 runs forward at full speed.
}

void mundur() {
  motor_DepanKiri.setSpeed(-255);  // Motor 1 runs backward at full speed.
  motor_DepanKanan.setSpeed(-255);   // Motor 2 runs forward at full speed.
  motor_BelakangKiri.setSpeed(-255);  // Motor 1 runs backward at full speed.
  motor_BelakangKanan.setSpeed(-255);   // Motor 2 runs forward at full speed.
}

void kiri() {
  motor_DepanKiri.setSpeed(255);  // Motor 1 runs backward at full speed.
  motor_DepanKanan.setSpeed(-255);   // Motor 2 runs forward at full speed.
  motor_BelakangKiri.setSpeed(255);  // Motor 1 runs backward at full speed.
  motor_BelakangKanan.setSpeed(-255);   // Motor 2 runs forward at full speed.
}

void kanan() {
  motor_DepanKiri.setSpeed(-255);  // Motor 1 runs backward at full speed.
  motor_DepanKanan.setSpeed(255);   // Motor 2 runs forward at full speed.
  motor_BelakangKiri.setSpeed(-255);  // Motor 1 runs backward at full speed.
  motor_BelakangKanan.setSpeed(255);   // Motor 2 runs forward at full speed.
}