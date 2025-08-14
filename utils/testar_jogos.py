# utils/testar_jogos.py
import time
from playwright.sync_api import Page
from utils.abrir_jogo_por_titulo import abrir_jogo_por_titulo
from utils.testar_carregamento_jogo import testar_carregamento_jogo
from utils.registrar_tempo import registrar_tempo
from utils.voltar_home import voltar_home

def testar_jogos(page: Page, jogos: list[dict], csv_nome: str, inicio_processo: float):
    tempo_anterior = time.time()
    
    for jogo in jogos:

        url_atual = page.url
        tipo = jogo["tipo"]
        # Ir para a página certa apenas se necessário
        if tipo == "lv" and "casino-live" not in url_atual:
            page.goto("https://www.apostou.bet.br/casino-live")
            page.wait_for_load_state("domcontentloaded")
            # Aguarda mais tempo para casino-live carregar completamente
            time.sleep(15)
            # Verifica se algum conteúdo de live casino carregou
            try:
                page.wait_for_selector("div, img, iframe, .game-item, [data-testid]", timeout=5000)
            except:
                print("⚠️  Casino-live pode não ter carregado completamente")
                time.sleep(5)  # aguarda mais um pouco
        elif tipo == "cs" and "casino-live" in url_atual:
            page.goto("https://www.apostou.bet.br")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(7)

        if abrir_jogo_por_titulo(page, jogo["title"]):
            t_fim = testar_carregamento_jogo(
                page=page,
                jogo=jogo,
                nome_csv=csv_nome,
                tempo_anterior=tempo_anterior,
                inicio_processo=inicio_processo
            )
        else:
            t_fim = time.time()
            registrar_tempo(csv_nome, f"🎰_{jogo['tipo']} > {jogo['provider']} > {jogo['title']} > ❌click", t_fim, tempo_anterior, inicio_processo)
        tempo_anterior = t_fim
        voltar_home(page)