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
from utils.slack_notifier       import enviar, CANAIS
from utils.format_slack         import formatar_sucesso, formatar_erros

# ── Configurações ───────────────────────────────────────────────────────────
JOGOS = [
    {"title":"Aviator","slug":"aviator","tipo":"casino","wait_value":"BRL"},
    {"title":"Master Joker","slug":"master_joker","tipo":"casino","wait_type":"network","wait_value":"gameService"},
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
        page     = context.new_page()

        # 1 ▪ Login -----------------------------------------------------------
        try:
            fazer_login(page, csv_nome, start_time)
        except Exception as e:
            erros["init"].append(str(e))

        # 2 ▪ Depósito PIX ----------------------------------------------------
        try:
            testar_deposito_pix(page, csv_nome, start_time)
        except Exception as e:
            erros["deposito"].append(str(e))

        # 3 ▪ Teste de jogos --------------------------------------------------
        testar_jogos(page, JOGOS, csv_nome, start_time)

        # 4 ▪ Métrica total e encerramento ------------------------------------
        total = time.time()
        registrar_tempo(csv_nome, "total_processo", total, start_time, start_time)
        print(f"\n✅ Fluxo concluído. Tempo total: {total - start_time:.2f}s")
        print(f"📊 Métricas salvas em: {csv_nome}")

        # 5 ▪ Varre CSV em busca de linhas "jogo_xxx (erro)"
        with open(csv_nome, encoding="utf-8") as f:
            for row in f:
                if "jogo_" in row and "(erro)" in row:
                    slug = row.split(",")[0].replace("jogo_", "")
                    erros["jogos"].append(slug)


        # 6 ▪ Envio ao Slack --------------------------------------------------
        
        # a. Mensagem de sucesso (sempre)
        #enviar(formatar_sucesso(csv_nome, JOGOS), "sucesso")

        # b. Mensagens de erro (se houver)
        #msg_init     = formatar_erros(csv_nome, "init",     JOGOS)
        #msg_deposito = formatar_erros(csv_nome, "deposito", JOGOS)
        #msg_jogos    = formatar_erros(csv_nome, "jogos",    JOGOS)

        #if msg_init:
        #    enviar(msg_init, "init")
        #if msg_deposito:
        #    enviar(msg_deposito, "deposito")
        #if msg_jogos:
        #    enviar(msg_jogos, "jogos")

        browser.close()


# ── Execução ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

    

