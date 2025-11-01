"""
Configurações do Cosmos [Ticket]
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Token do bot
BOT_TOKEN = os.getenv('DISCORD_TOKEN', 'MTQzMTM3MTQzODU4NTE1MTUyOQ.GmWyg7.4ZVzol_UVC14b4UB54SAJEywtWGIE8hbHcr6ao')

# Cores (em hexadecimal)
CORES = {
    'principal': 0x3e0b4d,    # Roxo cósmico
    'sucesso': 0x00ff00,      # Verde
    'erro': 0xff0000,         # Vermelho
    'aviso': 0xffff00,        # Amarelo
    'info': 0x00bfff          # Azul
}

# Emojis
EMOJIS = {
    'ticket': '🎫',
    'config': '⚙️',
    'sucesso': '✅',
    'erro': '❌',
    'aviso': '⚠️',
    'fechar': '🔒',
    'adicionar': '➕',
    'remover': '🗑️',
    'editar': '✏️',
    'voltar': '🔙',
    'enviar': '🚀'
}

# Mensagens padrão
MENSAGENS_PADRAO = {
    'abertura': 'Olá {user}! Sua solicitação foi recebida. Nossa equipe responderá em breve.',
    'fechamento': 'Ticket fechado por {user}.',
    'footer': 'Cosmos [Ticket] • Sistema estelar'
}

# Arquivos de banco de dados
DATABASE_FILES = {
    'paineis': 'paineis.json',
    'tickets': 'tickets.json'
}

# Configurações de timeout (em segundos)
TIMEOUTS = {
    'view_principal': 600,      # 10 minutos
    'view_configuracao': 600,   # 10 minutos
    'view_opcoes': 600,         # 10 minutos
    'modal': 300,               # 5 minutos
    'confirmacao': 60           # 1 minuto
}

# Limites
LIMITES = {
    'max_opcoes_botoes': 25,    # Limite do Discord
    'max_opcoes_dropdown': 25,  # Limite do Discord
    'max_paineis_guild': 50,    # Limite por servidor
    'max_titulo_embed': 256,    # Caracteres
    'max_descricao_embed': 4000 # Caracteres
}

# Configurações de log
LOG_CONFIG = {
    'formato': '[%(asctime)s] %(levelname)s: %(message)s',
    'data_formato': '%Y-%m-%d %H:%M:%S',
    'nivel': 'INFO'
}

# Permissões necessárias para o bot
PERMISSOES_NECESSARIAS = [
    'manage_channels',
    'send_messages',
    'embed_links',
    'read_message_history',
    'manage_messages',
    'view_channel'
]
