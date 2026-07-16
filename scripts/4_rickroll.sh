#!/bin/bash
echo "========================================"
echo "[+] INICIANDO PAYLOAD: AUTOMATED RICKROLL"
echo "========================================"
echo "[*] Alvo detetado via sessao ativa..."
echo "[*] Injetando comando no browser Debian..."

DISPLAY=:0 xdg-open "https://youtube.com" > /dev/null 2>&1 &

