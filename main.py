"""
main.py  –  Orquestra todo o fluxo:
1. Faz login
2. Mede tempo do depósito via PIX
3. Mede tempo de carregamento de cada jogo
4. Registra métricas em CSV
5. Dispara alertas no Slack conforme sucesso ou tipo de erro
"""

# ── Preparação ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())                       # carrega .env antes de tudo

import os, time
from datetime import datetime
from playwright.sync_api import sync_playwright

from utils.registrar_tempo      import registrar_tempo
from utils.fazer_login          import fazer_login
from utils.testar_deposito_pix  import testar_deposito_pix
from utils.testar_jogos         import testar_jogos
from utils.voltar_home          import voltar_home
from utils.reportar_slack       import reportar   # ← adicione no topo

# ── Configurações ───────────────────────────────────────────────────────────

JOGOS = [
    # Pragmatic
    {"provider": "pragmatic", "title": "Master Joker", "tipo": "casino", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pragmatic", "title": "Tigre Sortudo", "tipo": "casino", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pragmatic", "title": "Gates of Olympus", "tipo": "casino", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pragmatic", "title": "Super 7s", "tipo": "casino", "wait_type": "network", "wait_value": "gameService"},

    # Aviator Studio
    {"provider": "aviator_studio", "title": "Aviator", "tipo": "casino", "wait_value": "BRL"},

    # PG
    {"provider": "pg", "title": "Dragon Hatch 2", "tipo": "casino", "wait_value": "Começar"},
    {"provider": "pg", "title": "Fortune Rabbit", "tipo": "casino", "wait_value": "Começar"},
    {"provider": "pg", "title": "Pinata Wins", "tipo": "casino", "wait_value": "Começar"},
    {"provider": "pg", "title": "Fortune Tiger", "tipo": "casino", "wait_value": "Começar"},

    # Platipus
    {"provider": "platipus", "title": "Chilli Fiesta", "tipo": "casino", "wait_value": "Começar"},

    # Cassino ao vivo
    {"provider": "playtech", "title": "Roleta Brasileira", "tipo": "live", "wait_value": "Saldo"},
    {"provider": "evolution", "title": "Lightning Dice", "tipo": "live","wait_type": "network", "wait_value": "lightningdice.json"},
    {"provider": "pragmatic", "title": "Mega Roleta Brasileira", "tipo": "live", "wait_value": "SALDO"},
    {"provider": "evolution", "title": "Brazillian Bac Bo", "tipo": "live","wait_type": "network", "wait_value": "bacbo.json"},
    {"provider": "pragmatic", "title": "Brazilian ONE Blackjack", "tipo": "live", "wait_value": " Começar a Jogar "},
    {"provider": "playtech", "title": "Baccarat", "tipo": "live", "wait_value": "SALDO"},
]



# ── Função principal ────────────────────────────────────────────────────────
def main() -> None:
    start_time = time.time()
    csv_nome   = f"metricas_login_{datetime.now():%Y%m%d_%H%M%S}.csv"

    # Dicionário que acumula falhas
    erros = {"init": [], "deposito": [], "jogos": []}

    print("\n🟡 Iniciando Playwright...")
    with sync_playwright() as p:
        browser  = p.chromium.launch(headless=False)
        context  = browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": -25.4284, "longitude": -49.2733},
            locale="pt-BR"
        )

        inicio_processo = time.time()
        page = context.new_page()

        # 1 ▪ Login -----------------------------------------------------------
        try:
            fazer_login(page, csv_nome, start_time)
        except Exception as e:
            erros["init"].append(str(e))
                
        # 2 ▪ Depósito PIX ----------------------------------------------------
        try:
            testar_deposito_pix(page, csv_nome, start_time)
            voltar_home(page)
        except Exception as e:
            erros["deposito"].append(str(e))

        # 3 ▪ Teste de jogos --------------------------------------------------
        testar_jogos(page, JOGOS, csv_nome, start_time)

        # 4 ▪ Métrica total e encerramento ------------------------------------
        total = time.time()
        registrar_tempo(csv_nome, "total_processo", total, start_time, start_time)
        print(f"\n✅ Fluxo concluído. Tempo total: {total - start_time:.2f}s")
        print(f"📊 Métricas salvas em: {csv_nome}")

        reportar(csv_nome, inicio_processo)

        browser.close()


# ── Execução ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

    

