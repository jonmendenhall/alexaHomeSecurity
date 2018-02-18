// =========================
// import required libraries
// =========================

#include <avr/sleep.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "printf.h"


// ======================
// set required variables
// ======================

#define BASE_STATION_ADDRESS 0xE0E0E0E0F2
#define SENSOR_ID 1

RF24 radio(7, 8);


// =====================
// main startup function
// =====================

void setup() {

	// disable the ADC
	ADCSRA &= ~(1 << 7);
	SMCR |= (1 << 2);
	SMCR |= 1;

	pinMode(2, INPUT);		// set PIR sensor pin to INPUT
	digitalWrite(2, 1);		// set pull-up resistor for pin

	// setup nrf24l01 radio module
	radio.begin();
	radio.setPayloadSize(1);
	radio.setChannel(0x60);							// must be same for sensors and base station
	radio.setDataRate(RF24_1MBPS);					// must be same for sensors and base station
	radio.setPALevel(RF24_PA_LOW);					// set to low power for longer battery life
	radio.setAutoAck(true);
	radio.enableAckPayload();
	radio.enableDynamicPayloads();
	radio.openWritingPipe(BASE_STATION_ADDRESS);	// send data to the base station's address
	radio.setRetries(15, 15);
	radio.stopListening();
	radio.powerDown();								// power down until motion sensed

	attachInterrupt(0, wake, RISING);				// connect interrupt on sensor pin
}


// ==================
// main loop function 
// ==================

void loop() {

	// put the Arduino to sleep for low power consumption
	MCUCR |= (3 << 5);
	MCUCR = (MCUCR & ~(1 << 5)) | (1 << 6);
	__asm__ __volatile__("sleep");				// wait for interrupt to wake up

	// the Arduino has now been woken up by interrupt on sensor pin (MOTION SENSED)

	radio.powerUp();				// turn on the radio
	radio.write(SENSOR_ID, 1);		// send this sensor's id to the base station
	radio.powerDown();				// turn off the radio

	// Serial.write("1\n");
	// Serial.flush();
}

// only here because attachInterrupt needs a function

void wake() {}	// left empty so code goes straight to where it left off


