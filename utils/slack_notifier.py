# utils/slack_notifier.py
import os
from slack_sdk import WebClient, errors

BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("SLACK_BOT_TOKEN ausente")

client = WebClient(token=BOT_TOKEN)

CANAIS = {
    "sucesso":   os.getenv("BOT_SUCCESS"),        # ✅
    "init":      os.getenv("BOT_ERROR_INIT"),     # 🛑
    "deposito":  os.getenv("BOT_ERROR_DEPOSIT"),  # ⚠️
    "jogos":     os.getenv("BOT_ERROR_GAMES"),    # 🎮
}

def enviar(msg: str, categoria: str = "sucesso"):
    canal = CANAIS.get(categoria)
    if not canal:
        print(f"[Slack] Canal não configurado para '{categoria}'")
        return
    try:
        client.chat_postMessage(channel=canal, text=msg)
    except errors.SlackApiError as e:
        print(f"[Slack] Erro: {e.response['error']}")
