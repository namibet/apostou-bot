from utils.rules import validate_platform_load

def run_cassino_test(page):
    print("🎰 Testando plataforma: Cassino")
    page.click("text=Cassino")
    page.wait_for_timeout(5000)

    if not validate_platform_load(page):
        raise Exception("❌ Plataforma 'Cassino' falhou no carregamento")

    print("✅ Plataforma 'Cassino' carregou corretamente.")
