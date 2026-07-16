import time
import os
import sys
import subprocess
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

# Setup do Ecrã OLED e Botões
serial = i2c(port=1, address=0x3C)
device = sh1106(serial, width=128, height=64)

GPIO.setmode(GPIO.BCM)
buttons = {"CENTER": 16}
GPIO.setup(buttons["CENTER"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

def configurar_teclado_virtual():
    print("[*] Configurando driver usb_gadget conforme os repositorios da comunidade...")
    os.system("echo '' | sudo tee /sys/kernel/config/usb_gadget/g1/UDC > /dev/null 2>&1")
    os.system("sudo rm -rf /sys/kernel/config/usb_gadget/g1 > /dev/null 2>&1")
    time.sleep(0.4)
    
    comandos = [
        "sudo mkdir -p /sys/kernel/config/usb_gadget/g1",
        "echo 0x1d6b | sudo tee /sys/kernel/config/usb_gadget/g1/idVendor > /dev/null",
        "echo 0x0104 | sudo tee /sys/kernel/config/usb_gadget/g1/idProduct > /dev/null",
        "echo 0x0100 | sudo tee /sys/kernel/config/usb_gadget/g1/bcdDevice > /dev/null",
        "echo 0x0200 | sudo tee /sys/kernel/config/usb_gadget/g1/bcdUSB > /dev/null",
        "sudo mkdir -p /sys/kernel/config/usb_gadget/g1/strings/0x409",
        "echo 'fedcba9876543210' | sudo tee /sys/kernel/config/usb_gadget/g1/strings/0x409/serialnumber > /dev/null",
        "echo 'Apple Inc.' | sudo tee /sys/kernel/config/usb_gadget/g1/strings/0x409/manufacturer > /dev/null", 
        "echo 'Keyboard' | sudo tee /sys/kernel/config/usb_gadget/g1/strings/0x409/product > /dev/null",
        "sudo mkdir -p /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409",
        "echo 'Standard HID Keyboard' | sudo tee /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409/configuration > /dev/null",
        "sudo mkdir -p /sys/kernel/config/usb_gadget/g1/functions/hid.usb0",
        "echo 1 | sudo tee /sys/kernel/config/usb_gadget/g1/functions/hid.usb0/protocol > /dev/null",
        "echo 1 | sudo tee /sys/kernel/config/usb_gadget/g1/functions/hid.usb0/subclass > /dev/null",
        "echo 8 | sudo tee /sys/kernel/config/usb_gadget/g1/functions/hid.usb0/report_length > /dev/null",
        "echo -ne '\\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0' | sudo tee /sys/kernel/config/usb_gadget/g1/functions/hid.usb0/report_desc > /dev/null",
        "sudo ln -sf /sys/kernel/config/usb_gadget/g1/functions/hid.usb0 /sys/kernel/config/usb_gadget/g1/configs/c.1/",
        "echo '3f980000.usb' | sudo tee /sys/kernel/config/usb_gadget/g1/UDC > /dev/null",
        "sudo chmod 666 /dev/hidg0 > /dev/null 2>&1"
    ]
    for cmd in comandos: os.system(cmd)

def write_report(report):
    try:
        with open('/dev/hidg0', 'rb+', buffering=0) as fh:
            fh.write(report)
        return True
    except Exception as e:
        return False

def p_e_s(modificador, codigo_hid):
    write_report(bytes([modificador, 0, codigo_hid, 0, 0, 0, 0, 0]))
    time.sleep(0.05)
    write_report(bytes([0, 0, 0, 0, 0, 0, 0, 0])) 
    time.sleep(0.05)

def digitar_texto_cadenciado(texto):
    mapa_hid = {
        'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09, 'g': 0x0a,
        'h': 0x0b, 'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f, 'm': 0x10, 'n': 0x11,
        'o': 0x12, 'p': 0x13, 'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17, 'u': 0x18,
        'v': 0x19, 'w': 0x1a, 'x': 0x1b, 'y': 0x1c, 'z': 0x1d, ' ': 0x2c, '.': 0x37,
    }
    for char in texto.lower():
        if char in mapa_hid: 
            p_e_s(0, mapa_hid[char])
        time.sleep(0.05)

def verificar_conexao_real():
    try:
        estado = subprocess.check_output("cat /sys/class/udc/*/state", shell=True, text=True).strip().lower()
        return estado in ["configured", "powered", "default"]
    except: return False

configurar_teclado_virtual()

tick = 0

while True:
    if verificar_conexao_real(): break
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    draw.rectangle((1, 1, 126, 62), outline=255, fill=0)
    draw.ellipse((14, 12, 38, 36), fill=255)
    draw.ellipse((20, 9, 44, 33), fill=0)
    if tick % 2 == 0:
        draw.rectangle((76, 20, 100, 32), outline=255, fill=0)
        draw.rectangle((100, 23, 106, 29), fill=255)
    draw.text((12, 48), "CONECTA O CABO...", fill=255)
    device.display(image)
    if GPIO.input(buttons["CENTER"]) == GPIO.LOW: sys.exit(0)
    tick += 1
    time.sleep(0.4)

image_atk = Image.new("1", (128, 64))
draw_atk = ImageDraw.Draw(image_atk)
draw_atk.rectangle((1, 1, 126, 62), outline=255, fill=0)
draw_atk.text((22, 16), "BADUSB ACTIVE", fill=255)
draw_atk.text((16, 36), "INJECTING KEYS...", fill=255)
device.display(image_atk)

time.sleep(6.0)

p_e_s(0x08, 0x15) # 0x08 = Modificador GUI, 0x15 = 'R'
time.sleep(2.0)

digitar_texto_cadenciado("cmd")
time.sleep(0.5)

p_e_s(0, 0x28) # 0x28 = ENTER
time.sleep(2.5) 

digitar_texto_cadenciado("notepad")
time.sleep(0.5)

p_e_s(0, 0x28) # ENTER
time.sleep(2.5) # Aguarda o Bloco de Notas abrir

digitar_texto_cadenciado("ola mundo")
p_e_s(0, 0x28) # ENTER final

print("[+] Concluido.")
time.sleep(1.0)
