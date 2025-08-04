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
    nome_jogo  = jogo["slug"]
    wait_type  = jogo.get("wait_type",  "text")
    wait_val   = jogo.get("wait_value", "Começar")

    print(f"\n🎮 \033[33m{nome_jogo}\033[0m")
    start = time.time()

    try:
        if wait_type == "text":
            print(f"⏳ Aguardando texto '{wait_val}'…")
            page.frame_locator("iframe").first.locator(f"text={wait_val}") \
                .first.wait_for(timeout=20000)

        elif wait_type == "network":
            print(f"⏳ Aguardando requisição com '{wait_val}' na URL…")
            page.wait_for_response(
                lambda r: wait_val in r.url and r.status == 200,
                timeout=20000
            )

        else:
            raise ValueError(f"Estratégia desconhecida: {wait_type}")

        end = time.time()
        registrar_tempo(nome_csv, f"jogo_{nome_jogo}", end, tempo_anterior, inicio_processo)
        print(f"✅ Carregado em {end - start:.2f}s")
        return end

    except TimeoutError:
        end = time.time()
        registrar_tempo(nome_csv, f"jogo_{nome_jogo} (timeout)", end, tempo_anterior, inicio_processo)
        print(f"⏰ Timeout aguardando '{wait_val}' ({wait_type}) no jogo '{nome_jogo}'")
        return end

    except Exception as e:
        end = time.time()
        registrar_tempo(nome_csv, f"jogo_{nome_jogo} (erro)", end, tempo_anterior, inicio_processo)
        print(f"❌ Falha ao carregar '{nome_jogo}': {e}")
        return end
