# utils/formatador_slack.py
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import os

EMO_SUCESSO = ":white_check_mark:"
EMO_JOGOS   = "🕹️"
EMO_TOTAL   = ":stopwatch:"


def formatar_sucesso(csv_path: str | Path, jogos: List[Dict]) -> str:
    """
    Constrói mensagem Slack pegando:
      • delta  de cada etapa individual
      • tempo_total_segundos da linha total_processo
    """
    deltas: dict[str, float] = {}
    totais: dict[str, float] = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)              # ← usa nomes das colunas
        for row in reader:
            etapa   = row["etapa"].strip()
            try:
                total = float(row["tempo_total_segundos"])
                delta = float(row["tempo_delta_segundos"])
                totais[etapa]  = total
                deltas[etapa]  = delta
            except ValueError:
                continue                        # ignora células vazias

    # ── infraestrutura ──
    infra = [
        ("Home carregada",   deltas.get("carregamento_home", 0)),
        ("Pop-up de idade",  deltas.get("popup_idade", 0)),
        ("Cookies aceitos",  deltas.get("aceite_cookies", 0)),
        ("Clique login",     deltas.get("clique_login", 0)),
        ("Login submetido",  deltas.get("login_submetido", 0)),
        ("Depósito (QR code)", deltas.get("t_deposito", 0)),
    ]
    
    # ── total_process (vem da coluna tempo_total_segundos) ──
    total_proc = totais.get("total_processo", 0.0)

    # ── timeframe ──────────────────────────────────────────────
    # nome do arquivo:  metricas_login_YYYYMMDD_HHMMSS.csv
    ts_str   = os.path.basename(csv_path).split("_", 2)[2].replace(".csv", "")
    inicio   = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
    fim      = inicio + timedelta(seconds=total_proc)

    linhas = [
        f"{EMO_SUCESSO} *Execução:* {inicio:%d/%m/%Y %H:%M:%S} → {fim:%H:%M:%S}",
        "",
        "_Resumo de performance (segundos)_",
    ]

    for nome, seg in infra:
        linhas.append(f"• {nome} | {seg:.2f}")

    # ── jogos ──
    linhas.append(f"\n{EMO_JOGOS} *Jogos*")
    for jogo in jogos:
        etapa = f"jogo_{jogo['slug']}"
        if etapa in deltas:
            linhas.append(f"{EMO_SUCESSO} {jogo['title']} | {deltas[etapa]:.2f}")

    linhas.append(f"\n{EMO_TOTAL} *Tempo total: {total_proc:.2f}*")
    linhas.append("—" * 40)

    return "\n".join(linhas)


# utils/formatador_slack.py  (adicione abaixo)
def formatar_erros(csv_path: str | Path,
                   categoria: str,
                   jogos: List[Dict]) -> str:
    """
    Gera mensagem de erro para 'init', 'deposito' ou 'jogos'.
    Para jogos lista cada jogo com ❌ e o tempo até o timeout/erro.
    """
    linhas = []
    emoji_x = ":x:"      # ou :red_circle:

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            etapa  = row["etapa"].strip()
            delta  = row["tempo_delta_segundos"]
            if "(erro)" not in etapa:
                continue

            if categoria == "jogos" and etapa.startswith("jogo_"):
                slug = etapa.replace("jogo_", "").replace(" (erro)", "")
                # pega o title original
                title = next((j["title"] for j in jogos if j["slug"] == slug), slug)
                linhas.append(f"{emoji_x} {title} | {delta}")
            elif categoria == "deposito" and etapa.startswith("t_deposito"):
                linhas.append(f"{emoji_x} Depósito (QR code) | {delta}")
            elif categoria == "init" and not etapa.startswith(("jogo_", "t_deposito")):
                nome = etapa.replace(" (erro)", "")
                linhas.append(f"{emoji_x} {nome} | {delta}")

    header = {
        "jogos":      f":video_game: *Erros em jogos:*",
        "deposito":   f":bank: *Erro no depósito:*",
        "init":       f":warning: *Erros de inicialização:*"
    }[categoria]

    return "\n".join([header] + linhas) if linhas else ""
