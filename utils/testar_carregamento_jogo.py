# utils/testar_carregamento_jogo.py
import time
from playwright.sync_api import Page, TimeoutError
from utils.registrar_tempo import registrar_tempo

def testar_carregamento_jogo(page: Page, jogo: dict,
                             nome_csv: str, tempo_anterior: float,
                             inicio_processo: float) -> float:
    """
    Aguarda o carregamento de um jogo conforme a estratégia indicada em `jogo`.
    Estratégias:
      • text    → espera texto visível dentro de QUALQUER iframe
      • iframe  → espera iframe[name == wait_value] anexado e DOM pronto
      • network → espera requisição que contenha `wait_value` na URL
    """
    nome_jogo  = jogo["title"]
    wait_type  = jogo.get("wait_type",  "text")
    wait_val   = jogo.get("wait_value", "Começar")

    print(f"\n🎮 \033[33m{nome_jogo}\033[0m")
    start = time.time()

    try:
        if wait_type == "text":
            page.frame_locator("iframe").first.locator(f"text={wait_val}").first.wait_for(timeout=40000)
            print(f"⏳ Aguardando texto '{wait_val}'…")

        elif wait_type == "network":
            print(f"⏳ Aguardando iframe do jogo e requisição com '{wait_val}' na URL…")
            try:
                frame = page.frame_locator("iframe").first
                frame.locator("body").wait_for(timeout=40000)

                response = page.wait_for_event(
                    "response",
                    lambda r: wait_val in r.url and r.status == 200,
                    timeout=40000
                )
                print(f"✅ Requisição com '{wait_val}' detectada com sucesso: {response.url}")
            except Exception as e:
                print(f"❌ Falha ao detectar requisição: {e}")
                raise

        else:
            raise ValueError(f"Estratégia desconhecida: {wait_type}")

        end = time.time()
        
        registrar_tempo(nome_csv, f"🎰_{jogo['tipo']} > {jogo['provider']} > {jogo['title']}", end, start, inicio_processo)
        print(f"✅ Carregado em {end - start:.2f}s")

        return end

    except TimeoutError:
        end = time.time()
        registrar_tempo(nome_csv, f"🎰_{jogo['tipo']} > {jogo['provider']} > {jogo['title']} > ❌timeout", end, tempo_anterior, inicio_processo)
        print(f"⏰ Timeout aguardando '{wait_val}' ({wait_type}) no jogo '{nome_jogo}'")
        return end

    except Exception as e:
        end = time.time()
        registrar_tempo(nome_csv, f"🎰_{jogo['tipo']} > {jogo['provider']} > {jogo['title']} > ❌erro", end, tempo_anterior, inicio_processo)
        print(f"❌ Falha ao carregar '{nome_jogo}': {e}")
        return end
