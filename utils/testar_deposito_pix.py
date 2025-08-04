import time
from playwright.sync_api import Page
from utils.registrar_tempo import registrar_tempo

def testar_deposito_pix(page: Page, nome_csv: str, inicio_processo: float) -> float:
    """
    Testa quanto tempo leva desde o clique no botão de Depósito até a geração do QR Code Pix.

    Args:
        page (Page): Instância ativa da página Playwright.
        nome_csv (str): Caminho do arquivo CSV para registro de tempo.
        inicio_processo (float): Timestamp do início geral do processo.

    Returns:
        float: Timestamp do fim do processo de geração do QR Code.
    """
    print("\n💰 Iniciando fluxo de depósito via Pix...")
    start = time.time()
    
    try:
        print("⏳ Clicando no botão 'Depositar - PIX' da home...")
        page.locator("div.deposit-button:has-text('PIX')").click()

        page.wait_for_load_state("domcontentloaded")
        time.sleep(0.5)

        print("⏳ Clicando no botão 'Depositar' da tela de valor...")
        page.locator("button:has-text('Depositar')").click()

        print("⏳ Aguardando modal com texto 'Código Pix válido até:'...")
        page.locator("text=Código Pix válido até:").wait_for(timeout=10000)

        end = time.time()
        registrar_tempo(nome_csv, "💵_deposito", end, start, inicio_processo)
        print(f"✅ QR Code gerado em {end - start:.2f} segundos.\n")
        return end

    except Exception as e:
        end = time.time()
        registrar_tempo(nome_csv, "💵_deposito ❌(erro)", end, start, inicio_processo)
        return end
