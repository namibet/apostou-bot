import os
from dotenv import load_dotenv

load_dotenv()

def do_login(page):
    page.goto("https://apostou.bet.br")
    
    # Espera o botão de login aparecer
    page.wait_for_selector("text=Login", timeout=10000)
    page.click("text=Login")

    # Preenche e envia o formulário de login
    page.fill("input[name='email']", os.getenv("APOSTOU_USER"))
    page.fill("input[name='password']", os.getenv("APOSTOU_PASS"))
    page.click("button[type='submit']")

    # Espera a página carregar depois do login
    page.wait_for_load_state("networkidle")
