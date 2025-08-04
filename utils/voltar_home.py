import time
from playwright.sync_api import Page, TimeoutError

def voltar_home(page: Page):
    """
    Volta para a home da Apostou e aguarda até que o logo no rodapé seja carregado.

    Args:
        page (Page): Instância atual da página Playwright.
    """
    #print("↩️  Voltando para a home…")
    page.goto("https://apostou.bet.br")

    try:
        # Aguarda o logo no footer
        page.wait_for_selector('img[title="Logo"]', timeout=10000)
        time.sleep(2)  # pequeno buffer para garantir que tudo carregou
        print("↩️  Home Carregada")
    except TimeoutError:
        print("⚠️ Logo não encontrado – a home pode não ter carregado corretamente.")
