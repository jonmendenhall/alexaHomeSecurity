import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
 
GPIO.setmode(GPIO.BCM)
 
# pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0x00, 0x00, 0xc2, 0x00, 0x01]]
 
master = 0x0000000001

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(6, 10)
# radio.setPayloadSize(32)
radio.setChannel(0x00)
 
# radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)
# radio.setAutoAck(True)
# radio.enableDynamicPayloads()
# radio.enableAckPayload()
 
radio.openReadingPipe(0, master)
radio.printDetails()
 
radio.startListening()
 
while(1):
    # ackPL = [1]
    while not radio.available(0):
        time.sleep(1 / 100)
    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    print("Received: {}".format(receivedMessage))
 
    # print("Translating the receivedMessage into unicode characters")
    # string = ""
    # for n in receivedMessage:
    #     # Decode into standard unicode set
    #     if (n &gt;= 32 and n &lt;= 126):
    #         string += chr(n)
    # print(string)
    # radio.writeAckPayload(1, ackPL, len(ackPL))
    # print("Loaded payload reply of {}".format(ackPL))