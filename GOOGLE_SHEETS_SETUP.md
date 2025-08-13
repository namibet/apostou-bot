# Configuração Google Sheets

## Passo 1: Criar Service Account

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google Sheets API** e **Google Drive API**
4. Vá em **IAM & Admin** > **Service Accounts**
5. Clique **Create Service Account**
6. Dê um nome (ex: "apostou-bot-sheets")
7. Clique **Create and Continue**
8. Pule as permissões opcionais
9. Clique **Done**

## Passo 2: Gerar Chave JSON

1. Clique no service account criado
2. Vá na aba **Keys**
3. Clique **Add Key** > **Create new key**
4. Escolha **JSON** e clique **Create**
5. Salve o arquivo JSON em local seguro

## Passo 3: Criar Planilha Google Sheets

1. Acesse [Google Sheets](https://sheets.google.com/)
2. Crie uma nova planilha
3. Anote o ID da planilha (na URL: `https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/edit`)
4. Compartilhe a planilha com o email do service account (encontrado no JSON)
5. Dê permissão de **Editor**

## Passo 4: Configurar Variáveis de Ambiente

Adicione no seu `.env`:

```bash
# Google Sheets
GOOGLE_SHEET_ID=seu_google_sheet_id_aqui
GOOGLE_CREDENTIALS_FILE=caminho/para/service-account.json
```

## Estrutura da Planilha

A planilha será criada automaticamente com as seguintes colunas:

- **timestamp_init**: Início da execução
- **timestamp_end**: Fim da execução  
- **total_processo**: Tempo total em segundos
- **home**: Tempo carregamento home
- **idade**: Tempo popup idade
- **cookies**: Tempo aceitar cookies
- **login**: Tempo clicar login
- **submit**: Tempo submeter formulário
- **deposito**: Tempo teste depósito PIX
- **lv_provider_game**: Jogos live (colunas dinâmicas)
- **cs_provider_game**: Jogos casino (colunas dinâmicas)

## Teste

Execute o bot normalmente:

```bash
python main.py
```

Se configurado corretamente, verá:
- ✅ Conectado ao Google Sheets
- 📊 Dados enviados para Google Sheets

## Troubleshooting

**Erro de autenticação:**
- Verifique se o arquivo JSON existe e o caminho está correto
- Confirme que compartilhou a planilha com o service account

**Erro de permissões:**
- Verifique se as APIs estão ativadas no Google Cloud
- Confirme que o service account tem acesso à planilha

**Planilha não encontrada:**
- Verifique se o GOOGLE_SHEET_ID está correto
- Confirme que a planilha existe e está acessível