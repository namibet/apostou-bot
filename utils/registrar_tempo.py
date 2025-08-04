import os
import csv

def registrar_tempo(nome_arquivo, nome_etapa, tempo_total, tempo_anterior, inicio_processo):
    """
    Registra uma linha de tempo no arquivo CSV.

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

    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if escrever_cabecalho:
            writer.writerow(["etapa", "tempo_total_segundos", "tempo_delta_segundos"])
        writer.writerow([nome_etapa, tempo_relativo, tempo_delta])
