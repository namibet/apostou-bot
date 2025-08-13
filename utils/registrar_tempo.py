import os
import csv
from utils.google_sheets import sheets_manager

def registrar_tempo(nome_arquivo, nome_etapa, tempo_total, tempo_anterior, inicio_processo):
    """
    Registra uma linha de tempo no arquivo CSV e envia para Google Sheets.

    Args:
        nome_arquivo (str): Caminho do CSV.
        nome_etapa (str): Nome da etapa a registrar.
        tempo_total (float): Timestamp do momento atual.
        tempo_anterior (float): Timestamp do evento anterior.
        inicio_processo (float): Timestamp do início do script para calcular tempo relativo.
    """
    tempo_delta = round(tempo_total - tempo_anterior, 2)
    tempo_relativo = round(tempo_total - inicio_processo, 2)
    escrever_cabecalho = not os.path.exists(nome_arquivo)

    # Registra no CSV (mantém funcionalidade original)
    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if escrever_cabecalho:
            writer.writerow(["etapa", "tempo_total_segundos", "tempo_delta_segundos"])
        writer.writerow([nome_etapa, tempo_relativo, tempo_delta])
    
    # Registra no Google Sheets (nova funcionalidade)
    try:
        sheets_manager.registrar_etapa(nome_etapa, tempo_delta, tempo_total)
    except Exception as e:
        print(f"⚠️ Erro enviando para Google Sheets: {e}")

def iniciar_execucao_sheets(timestamp_init: float):
    """
    Inicia uma nova execução no Google Sheets.
    Deve ser chamado no início de cada execução do bot.
    """
    try:
        if sheets_manager.conectar():
            sheets_manager.iniciar_execucao(timestamp_init)
    except Exception as e:
        print(f"⚠️ Erro iniciando execução no Sheets: {e}")

def finalizar_execucao_sheets():
    """
    Finaliza a execução atual e envia dados para Google Sheets.
    Deve ser chamado no final de cada execução do bot.
    """
    try:
        sheets_manager.finalizar_execucao()
    except Exception as e:
        print(f"⚠️ Erro finalizando execução no Sheets: {e}")
