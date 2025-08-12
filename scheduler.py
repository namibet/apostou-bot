"""
scheduler.py - Gerenciador de execuções periódicas do bot

Executa o main.py em intervalos configuráveis, garantindo limpeza de memória
entre as execuções para evitar sobrecarga.
"""

import os
import time
import gc
import subprocess
import sys
import csv
import glob
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Carrega variáveis de ambiente
load_dotenv(find_dotenv())

def analisar_resultados() -> tuple[int, int]:
    """
    Analisa o CSV mais recente e conta sucessos e falhas.
    
    Returns:
        tuple[int, int]: (sucessos, falhas)
    """
    try:
        # Encontra o CSV mais recente
        csvs = glob.glob("metricas_login_*.csv")
        if not csvs:
            return 0, 0
            
        csv_mais_recente = max(csvs, key=os.path.getctime)
        
        sucessos = 0
        falhas = 0
        
        with open(csv_mais_recente, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                etapa = row.get('etapa', '')
                if '❌' in etapa:
                    falhas += 1
                elif any(emoji in etapa for emoji in ['🏠', '💵', '🎰']):
                    sucessos += 1
                    
        return sucessos, falhas
        
    except Exception:
        return 0, 0

def executar_bot() -> bool:
    """
    Executa o bot via subprocess para garantir isolamento completo de memória.
    
    Returns:
        bool: True se executou com sucesso, False se houve erro
    """
    try:
        # Configura encoding para Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Executa o main.py como subprocess independente
        resultado = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=1800,  # timeout de 30 minutos
            env=env,
            encoding='utf-8',
            errors='ignore'  # Ignora caracteres problemáticos
        )
        
        if resultado.returncode == 0:
            return True
        else:
            print(f"ERRO {resultado.returncode}")
            if resultado.stderr:
                print(resultado.stderr[-100:])  # últimas 100 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False
    except Exception as e:
        print(f"FALHA: {e}")
        return False

def executar_loop() -> None:
    """
    Loop principal que executa o bot em intervalos configuráveis.
    """
    intervalo_minutos = int(os.getenv("INTERVALO_MINUTOS", "2"))
    intervalo_segundos = intervalo_minutos * 60
    
    print(f"Bot Scheduler - Intervalo: {intervalo_minutos}min | Ctrl+C para parar")
    
    execucao = 1
    
    try:
        while True:
            agora = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{agora}] Execucao #{execucao}... ", end="")
            
            processo_ok = executar_bot()
            
            if processo_ok:
                # Analisa o CSV para contar sucessos e falhas reais
                sucessos, falhas = analisar_resultados()
                print(f"OK | S:{sucessos} F:{falhas}")
            else:
                print("FALHOU")
            
            gc.collect()
            
            proxima = datetime.fromtimestamp(time.time() + intervalo_segundos)
            print(f"Proxima: {proxima.strftime('%H:%M:%S')}")
            
            time.sleep(intervalo_segundos)
            execucao += 1
            
    except KeyboardInterrupt:
        print(f"\nFinalizando... Total execucoes: {execucao-1}")
        # Mostra estatísticas finais do último CSV
        sucessos, falhas = analisar_resultados()
        if sucessos + falhas > 0:
            print(f"Ultima execucao: S:{sucessos} F:{falhas} | Taxa: {(sucessos/(sucessos+falhas)*100):.1f}%")

if __name__ == "__main__":
    executar_loop()