from playwright.sync_api import sync_playwright
import os

def init_browser():
    p = sync_playwright().start()
    
    # Apenas argumentos para desabilitar cache
    chrome_args = [
        '--disable-application-cache',
        '--disable-disk-cache',
        '--disable-http-cache',
        '--disable-memory-cache',
        '--disk-cache-size=0'
    ]
    
    # Usa Chrome se disponível, senão Chromium
    chrome_path = '/usr/bin/google-chrome'
    
    if os.path.exists(chrome_path):
        browser = p.chromium.launch(
            headless=False,
            executable_path=chrome_path,
            args=chrome_args
        )
    else:
        browser = p.chromium.launch(
            headless=False,
            args=chrome_args
        )
    
    context = browser.new_context()
    page = context.new_page()
    
    return browser, page
