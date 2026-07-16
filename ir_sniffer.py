#!/usr/bin/env python3
import sys
import time
import json
import os
import pigpio

PINO_RECETOR = 24
FICHEIRO_BOTOES = "botoes_ir.json"

pi = pigpio.pi()
if not pi.connected:
    sys.exit(1)

pi.set_mode(PINO_RECETOR, pigpio.INPUT)

tempos_sinal = []
ultimo_tick = None

def callback_recetor(gpio, nivel, tick):
    global ultimo_tick, tempos_sinal
    if ultimo_tick is not None:
        duracao = pigpio.tickDiff(ultimo_tick, tick)
        tempos_sinal.append(duracao)
    ultimo_tick = tick

# Liga o recetor KS0026
cb = pi.callback(PINO_RECETOR, pigpio.EITHER_EDGE, callback_recetor)

# Fica em loop até detetar que o utilizador carregou no botão do comando
while len(tempos_sinal) < 10:
    time.sleep(0.05)

time.sleep(0.6)
cb.cancel()

if os.path.exists(FICHEIRO_BOTOES):
    try:
        with open(FICHEIRO_BOTOES, 'r') as f:
            base_botoes = json.load(f)
    except:
        base_botoes = {}
else:
    base_botoes = {}

proximo_id = 1
while f"sinal {proximo_id}" in base_botoes:
    proximo_id += 1

nome_final_sinal = f"sinal {proximo_id}"

# Adiciona o novo sinal capturado sem apagar os anteriores
base_botoes[nome_final_sinal] = tempos_sinal

# Guarda a lista completa atualizada de volta no ficheiro JSON
with open(FICHEIRO_BOTOES, 'w') as f:
    json.dump(base_botoes, f, indent=4)

pi.stop()

# Envia o nome exato gerado para o menu principal saber o que foi gravado
print(nome_final_sinal.upper())
