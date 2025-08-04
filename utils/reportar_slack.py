# utils/reportar_slack.py
"""
Lê o CSV de métricas e dispara mensagens no Slack
conforme o prefixo da etapa e presença de ❌.
"""
import csv
import time
from pathlib import Path
from datetime import datetime
from utils.slack_notifier import enviar   # já existente

CABECALHO = {
    "sucesso":  ":white_check_mark: *Etapas OK:*",
    "init":     ":warning: *Falhas de inicialização:*",
    "deposito": ":bank: *Falha no depósito:*",
    "jogos":    ":joystick: *Falhas em jogos:*",
}

# prefixo 🏠_, 💵_, 🎰_  → canal para erros
ERRO_CANAL = {"🏠": "init", "💵": "deposito", "🎰": "jogos"}

def reportar(csv_path: str | Path, inicio_processo: float) -> None:

    filas = {k: [] for k in CABECALHO}          # sucesso / init / deposito / jogos

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            etapa  = row["etapa"].strip()
            delta  = float(row["tempo_delta_segundos"])
            linha  = f"{etapa} | {delta:.2f}s"

            erro   = "❌" in etapa
            prefix = etapa[0]   # pega só o emoji no começo

            if erro:
                canal = ERRO_CANAL.get(prefix)  # init / deposito / jogos
                if canal:
                    filas[canal].append(linha)
            else:
                if prefix in {"🏠", "💵", "🎰"}:   # só etapas de teste
                    filas["sucesso"].append(linha)

    fim = time.time()
    duracao = round(fim - inicio_processo, 2)

    inicio_fmt = datetime.fromtimestamp(inicio_processo).strftime("%H:%M:%S")
    fim_fmt    = datetime.fromtimestamp(fim).strftime("%H:%M:%S")

    timestamp_msg = f"_Início: {inicio_fmt} | Fim: {fim_fmt} | Duração: {duracao:.2f}s_"

    # dispara apenas se houver conteúdo
    for canal, linhas in filas.items():
        if linhas:
            enviar("\n".join([CABECALHO[canal], timestamp_msg, *linhas]), canal)

