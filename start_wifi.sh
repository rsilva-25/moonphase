#!/bin/bash

PROJECT_PATH="/home/pi/flipper-moon"

sudo cp $PROJECT_PATH/index.html /var/www/html/index.html

# desliga Wi-Fi normal
sudo ifconfig wlan0 down

# dara serviços que possam interferir
sudo systemctl stop NetworkManager 2>/dev/null
sudo systemctl stop wpa_supplicant 2>/dev/null
sudo systemctl stop dhcpcd 2>/dev/null

# mostra a interface e define IP fixo
sudo ifconfig wlan0 up
sudo ifconfig wlan0 10.0.0.1 netmask 255.255.255.0

# ativa hotspot
sudo systemctl start hostapd
sudo systemctl start dnsmasq

# garantir que o hotspot fique ligado
sleep 5


sudo systemctl stop apache2
sudo systemctl restart lighttpd

# inicia servidor web
sudo systemctl restart lighttpd

# portal cativo
sudo /usr/sbin/iptables -t nat -F
sudo /usr/sbin/iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
# redireciona tráfego DNS
sudo /usr/sbin/iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT --to-destination 10.0.0.1

sudo /usr/sbin/iptables -t nat -A POSTROUTING -j MASQUERADE

echo "Hotspot ativo!!!"
