import os
import time
from playwright.sync_api import Page

from utils.registrar_tempo import registrar_tempo  # ajuste o path conforme sua estrutura

def fazer_login(page: Page, csv_nome: str, start_time: float) -> float:
    """
    Executa o fluxo completo de login na plataforma Apostou.

    Args:
        page (Page): Página atual do Playwright.
        csv_nome (str): Caminho para o arquivo CSV onde os tempos serão registrados.
        start_time (float): Timestamp do início do processo.

    Returns:
        float: Timestamp do fim do login (para ser usado como base do próximo passo).
    """
    page.goto("https://apostou.bet.br")
    page.wait_for_load_state("domcontentloaded")

    t_home = time.time()
    registrar_tempo(csv_nome, "carregamento_home", t_home, start_time, start_time)

    # Confirma idade
    try:
        page.wait_for_selector("button.mat-flat-button:has-text('Sim')", timeout=8000)
        page.click("button.mat-flat-button:has-text('Sim')")
    except:
        pass

    t_idade = time.time()
    registrar_tempo(csv_nome, "popup_idade", t_idade, t_home, start_time)

    # Aceita cookies
    try:
        page.click("button[data-cy='cookies-accept-button']:has-text('Aceitar todos')", timeout=5000)
    except:
        pass

    t_cookies = time.time()
    registrar_tempo(csv_nome, "aceite_cookies", t_cookies, t_idade, start_time)

    # Clica no botão Entrar
    for _ in range(3):
        try:
            page.wait_for_selector("text=Entrar", timeout=5000)
            page.locator("text=Entrar").nth(0).click(force=True)
            break
        except:
            time.sleep(1)

    t_click_login = time.time()
    registrar_tempo(csv_nome, "clique_login", t_click_login, t_cookies, start_time)

    # Preenche os campos e envia login
    try:
        page.wait_for_selector("input.form-control", timeout=8000)
        inputs = page.locator("input.form-control")

        user = os.getenv("APOSTOU_USER")
        senha = os.getenv("APOSTOU_PASS")

        inputs.nth(0).fill(user)
        inputs.nth(1).fill(senha)

        botao_entrar = page.locator("button.global_login__sign-in-btn")
        botao_entrar.wait_for(state="visible", timeout=8000)
        botao_entrar.hover()
        botao_entrar.click()
    except:
        pass

    t_login = time.time()
    registrar_tempo(csv_nome, "login_submetido", t_login, t_click_login, start_time)

    try:
        page.wait_for_selector("div.deposit-button.deposit_button_themed", timeout=15000)
    except:
        pass

    return t_login
