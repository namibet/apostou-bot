from playwright.sync_api import sync_playwright

def init_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)  # ou headless=True pra rodar invisível
    context = browser.new_context()
    page = context.new_page()
    return browser, page
