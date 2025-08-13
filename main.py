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

from utils.registrar_tempo      import registrar_tempo, iniciar_execucao_sheets, finalizar_execucao_sheets
from utils.fazer_login          import fazer_login
from utils.testar_deposito_pix  import testar_deposito_pix
from utils.testar_jogos         import testar_jogos
from utils.voltar_home          import voltar_home
from utils.reportar_slack       import reportar   # ← adicione no topo

# ── Configurações ───────────────────────────────────────────────────────────

JOGOS = [
    # Pragmatic
    {"provider": "pgmt", "title": "Master Joker", "tipo": "cs", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pgmt", "title": "Tigre Sortudo", "tipo": "cs", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pgmt", "title": "Gates of Olympus", "tipo": "cs", "wait_type": "network", "wait_value": "gameService"},
    {"provider": "pgmt", "title": "Super 7s", "tipo": "cs", "wait_type": "network", "wait_value": "gameService"},

    # Aviator Studio
    {"provider": "avst", "title": "Aviator", "tipo": "cs", "wait_value": "BRL"},

    # PG
    {"provider": "pg", "title": "Dragon Hatch 2", "tipo": "cs", "wait_value": "Começar"},
    {"provider": "pg", "title": "Fortune Rabbit", "tipo": "cs", "wait_value": "Começar"},
    {"provider": "pg", "title": "Pinata Wins", "tipo": "cs", "wait_value": "Começar"},
    {"provider": "pg", "title": "Fortune Tiger", "tipo": "cs", "wait_value": "Começar"},

    # Platipus
    {"provider": "pltp", "title": "Chilli Fiesta", "tipo": "cs", "wait_value": "Começar"},

    # Cassino ao vivo
    {"provider": "ptech", "title": "Roleta Brasileira", "tipo": "lv", "wait_value": "Saldo"},
    {"provider": "evol", "title": "Lightning Dice", "tipo": "lv","wait_type": "network", "wait_value": "lightningdice.json"},
    {"provider": "pgmt", "title": "Mega Roleta Brasileira", "tipo": "lv", "wait_value": "SALDO"},
    {"provider": "evol", "title": "Brazillian Bac Bo", "tipo": "lv","wait_type": "network", "wait_value": "bacbo.json"},
    {"provider": "pgmt", "title": "Brazilian ONE Blackjack", "tipo": "lv", "wait_value": " Começar a Jogar "},
    {"provider": "ptech", "title": "Baccarat", "tipo": "lv", "wait_value": "SALDO"},
]


# ── Função principal ────────────────────────────────────────────────────────
def main() -> None:
    start_time = time.time()
    
    # Garante que a pasta metricas existe
    os.makedirs("metricas", exist_ok=True)
    
    csv_nome   = f"metricas/metricas_login_{datetime.now():%Y%m%d_%H%M%S}.csv"

    # Inicia execução no Google Sheets
    iniciar_execucao_sheets(start_time)

    # Dicionário que acumula falhas
    erros = {"init": [], "deposito": [], "jogos": []}

    print("\n🟡 Iniciando Playwright...")
    with sync_playwright() as p:
        browser  = p.chromium.launch(headless=True)
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
        
        # Finaliza execução no Google Sheets
        finalizar_execucao_sheets()

        browser.close()


# ── Execução ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

    

