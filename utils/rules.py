def validate_platform_load(page):
    try:
        # Exemplo: checa se alguma seção visível foi carregada
        return page.locator("div#conteudo").is_visible(timeout=3000)
    except:
        return False
