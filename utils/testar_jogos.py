# utils/testar_jogos.py
import time
from playwright.sync_api import Page
from utils.abrir_jogo_por_titulo import abrir_jogo_por_titulo
from utils.testar_carregamento_jogo import testar_carregamento_jogo
from utils.registrar_tempo import registrar_tempo

def testar_jogos(page: Page, jogos: list[dict], csv_nome: str, inicio_processo: float):
    tempo_anterior = inicio_processo

    for jogo in jogos:
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
            registrar_tempo(csv_nome, f"jogo_{jogo['slug']} (falha_click)",
                            t_fim, tempo_anterior, inicio_processo)

        tempo_anterior = t_fim

        print("Voltando para a home…")
        page.goto("https://apostou.bet.br")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(7)
