def abrir_jogo_por_titulo(page, titulo_jogo):
    """
    Localiza e clica no jogo com base no atributo title da tag <img>.

    Args:
        page (playwright.sync_api.Page): Página ativa do navegador.
        titulo_jogo (str): Texto exato do atributo title no <img> do jogo.

    Returns:
        bool: True se o clique for bem-sucedido, False caso contrário.
    """
    imagens = page.locator(f'img[title="{titulo_jogo}"]')
    count = imagens.count()
    
    #print(f"[DEBUG] Encontradas {count} imagens com title='{titulo_jogo}'")
    
    for i in range(count):
        try:
            imagem = imagens.nth(i)
            imagem.wait_for(state="visible", timeout=3000)

            elemento_clicavel = imagem.locator("xpath=ancestor::app-casino-item-portrait[1]")
            elemento_clicavel.scroll_into_view_if_needed()
            elemento_clicavel.click()
            return True
        except:
            continue

    return False
