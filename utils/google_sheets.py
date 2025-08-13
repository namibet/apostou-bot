# utils/google_sheets.py
"""
Integração com Google Sheets para registrar métricas de performance.

Estrutura da planilha:
- timestamp_init: Início do processo
- timestamp_end: Fim da última etapa registrada  
- total_processo: Tempo total em segundos
- home, idade, cookies, login, submit: Etapas de login
- deposito: Tempo do depósito PIX
- cs_*, lv_*: Jogos de casino e live (colunas dinâmicas)
"""

import os
import gspread
from google.auth.exceptions import DefaultCredentialsError
from datetime import datetime
from typing import Optional, Dict, Any

class GoogleSheetsManager:
    """Gerenciador de integração com Google Sheets"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.current_row_data = {}
        self.timestamp_init = None
        
    def conectar(self) -> bool:
        """
        Conecta ao Google Sheets usando service account ou OAuth.
        
        Returns:
            bool: True se conectou com sucesso
        """
        try:
            # Tenta usar service account primeiro
            credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
            if credentials_file and os.path.exists(credentials_file):
                self.gc = gspread.service_account(filename=credentials_file)
            else:
                # Fallback para OAuth (requer configuração adicional)
                self.gc = gspread.oauth()
                
            # Conecta à planilha especificada
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            if not sheet_id:
                print("❌ GOOGLE_SHEET_ID não configurado no .env")
                return False
                
            self.sheet = self.gc.open_by_key(sheet_id)
            
            # Usa a primeira aba ou cria se não existir
            try:
                self.worksheet = self.sheet.get_worksheet(0)
            except IndexError:
                self.worksheet = self.sheet.add_worksheet(title="metricas", rows="1000", cols="50")
            
            # Garante que o cabeçalho existe
            self._garantir_cabecalho()
            
            print("✅ Conectado ao Google Sheets")
            return True
            
        except DefaultCredentialsError:
            print("❌ Erro de autenticação Google - configure as credenciais")
            return False
        except Exception as e:
            print(f"❌ Erro conectando Google Sheets: {e}")
            return False
    
    def _garantir_cabecalho(self):
        """Garante que o cabeçalho está presente na planilha"""
        try:
            primeira_linha = self.worksheet.row_values(1)
            if not primeira_linha or primeira_linha[0] != "timestamp_init":
                cabecalho = [
                    "timestamp_init", "timestamp_end", "total_processo",
                    "home", "idade", "cookies", "login", "submit", "deposito"
                ]
                self.worksheet.insert_row(cabecalho, 1)
                print("📋 Cabeçalho criado no Google Sheets")
        except Exception as e:
            print(f"⚠️ Erro criando cabeçalho: {e}")
    
    def iniciar_execucao(self, timestamp_init: float):
        """
        Inicia uma nova execução e prepara a linha de dados.
        
        Args:
            timestamp_init: Timestamp do início da execução
        """
        self.timestamp_init = timestamp_init
        self.current_row_data = {
            "timestamp_init": datetime.fromtimestamp(timestamp_init).strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp_end": "",
            "total_processo": 0,
            "home": 0,
            "idade": 0, 
            "cookies": 0,
            "login": 0,
            "submit": 0,
            "deposito": 0
        }
    
    def registrar_etapa(self, nome_etapa: str, tempo_delta: float, timestamp_atual: float):
        """
        Registra uma etapa na linha atual de dados.
        
        Args:
            nome_etapa: Nome da etapa (ex: "🏠_home", "💵_deposito")
            tempo_delta: Tempo da etapa em segundos
            timestamp_atual: Timestamp atual
        """
        if not self.current_row_data:
            return
            
        # Atualiza timestamp_end
        self.current_row_data["timestamp_end"] = datetime.fromtimestamp(timestamp_atual).strftime('%Y-%m-%d %H:%M:%S')
        
        # Mapeia etapas para colunas
        if nome_etapa.startswith("🏠_"):
            etapa = nome_etapa.replace("🏠_", "").replace(" ❌(erro)", "")
            if etapa in self.current_row_data:
                self.current_row_data[etapa] = tempo_delta
                
        elif nome_etapa.startswith("💵_"):
            self.current_row_data["deposito"] = tempo_delta
            
        elif nome_etapa.startswith("🎰_"):
            # Para jogos, cria coluna dinâmica
            # Ex: "🎰_lv > ptech > Baccarat" vira "lv_ptech_Baccarat"
            partes = nome_etapa.replace("🎰_", "").split(" > ")
            if len(partes) >= 3:
                coluna = f"{partes[0]}_{partes[1]}_{partes[2]}".replace(" ", "_")
                # Remove caracteres problemáticos
                coluna = "".join(c for c in coluna if c.isalnum() or c == "_")
                self.current_row_data[coluna] = tempo_delta
                
        elif nome_etapa == "total_processo":
            self.current_row_data["total_processo"] = tempo_delta
    
    def finalizar_execucao(self) -> bool:
        """
        Envia a linha completa para o Google Sheets.
        
        Returns:
            bool: True se enviou com sucesso
        """
        if not self.gc or not self.worksheet or not self.current_row_data:
            return False
            
        try:
            # Obtém cabeçalho atual da planilha
            cabecalho_atual = self.worksheet.row_values(1)
            
            # Adiciona novas colunas se necessário
            for coluna in self.current_row_data.keys():
                if coluna not in cabecalho_atual:
                    cabecalho_atual.append(coluna)
            
            # Atualiza cabeçalho se mudou
            if len(cabecalho_atual) > len(self.worksheet.row_values(1)):
                self.worksheet.update('1:1', [cabecalho_atual])
            
            # Prepara linha de dados na ordem do cabeçalho
            linha_dados = []
            for coluna in cabecalho_atual:
                valor = self.current_row_data.get(coluna, 0)
                linha_dados.append(valor)
            
            # Adiciona a linha na planilha
            self.worksheet.append_row(linha_dados)
            
            # Limpa dados da execução atual
            self.current_row_data = {}
            self.timestamp_init = None
            
            print(f"📊 Dados enviados para Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Erro enviando dados para Sheets: {e}")
            return False

# Instância global para ser usada em todo o projeto
sheets_manager = GoogleSheetsManager()