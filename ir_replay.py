#!/usr/bin/env python3
import sys
import time
import json
import os
import pigpio

PINO_EMISSOR = 18
FICHEIRO_BOTOES = "botoes_ir.json"

if len(sys.argv) < 2:
    print("[ERRO] Nome do botão não especificado.")
    sys.exit(1)

nome_botao = sys.argv[1].lower()

if not os.path.exists(FICHEIRO_BOTOES):
    sys.exit(1)

with open(FICHEIRO_BOTOES, 'r') as f:
    base_botoes = json.load(f)

if nome_botao not in base_botoes:
    sys.exit(1)

duracoes = base_botoes[nome_botao]

pi = pigpio.pi()
if not pi.connected:
    sys.exit(1)

pi.set_mode(PINO_EMISSOR, pigpio.OUTPUT)

try:
    
    # Configura a frequência base de 38kHz no pino 18
    pi.set_PWM_frequency(PINO_EMISSOR, 38000)
    
    # Obtém o tempo inicial de alta precisão do sistema
    tempo_alvo = time.time()
    estado_alto = True
    
    for microsegundos in duracoes:
        tempo_alvo += (microsegundos / 1000000.0)
        
        if estado_alto:
            pi.set_PWM_dutycycle(PINO_EMISSOR, 128)
            estado_alto = False
        else:
            pi.set_PWM_dutycycle(PINO_EMISSOR, 0)
            estado_alto = True
            
        while time.time() < tempo_alvo:
            pass

    pi.set_PWM_dutycycle(PINO_EMISSOR, 0)
    print("SUCESSO")

except Exception as e:
    print(f"{e}")
finally:
    pi.set_PWM_dutycycle(PINO_EMISSOR, 0)
    pi.stop()
