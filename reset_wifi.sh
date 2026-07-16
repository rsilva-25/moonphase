#!/bin/bash

# desliga serviços do hotspot 
sudo killall hostapd 2>/dev/null
sudo killall dnsmasq 2>/dev/null

# ativa o wifi
sudo ifconfig wlan0 down
sleep 1
sudo ifconfig wlan0 up
sleep 1

# reinicia o serviço de rede
sudo systemctl restart NetworkManager 2>/dev/null
sudo systemctl restart dhcpcd 2>/dev/null

# espera o Pi voltar
sleep 3


echo "VOLTOU A NET"
