import disnake
from disnake.ext import commands
import json
import os
from typing import Dict, List, Optional
from views import *
from ticket_system import *
from opcoes_view import *
from modals import *
from opcoes_modals import *
from config import *

# Configurações
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.InteractionBot(intents=intents)

# Banco de dados simulado (JSON)
DATABASE_FILE = "paineis.json"
TICKETS_FILE = "tickets.json"

def load_data(file: str) -> Dict:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(file: str, data: Dict):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Estrutura de dados do painel
def create_panel_structure(guild_id: int, panel_id: str) -> Dict:
    return {
        "guild_id": guild_id,
        "panel_id": panel_id,
        "canal_id": None,
        "mensagem_id": None,
        "embed": {
            "titulo": "🎫 Sistema de Tickets",
            "descricao": "Selecione uma opção abaixo para abrir um ticket.",
            "cor": 0x3e0b4d,
            "imagem": None,
            "thumbnail": None,
            "autor": None,
            "footer": "Cosmos [Ticket] • Sistema estelar"
        },
        "opcoes": [],
        "tipo_exibicao": "dropdown",
        "categoria_id": None,
        "cargo_suporte_id": None,
        "log_canal_id": None,
        "mensagem_abertura": "Olá {user}! Sua solicitação foi recebida. Nossa equipe responderá em breve.",
        "mensagem_fechamento": "Ticket fechado por {user}."
    }

@bot.event
async def on_ready():
    print(f'✨ {bot.user} está online!')
    print(f'🌌 Cosmos [Ticket] carregado com sucesso!')

# Comando principal
@bot.slash_command(
    name="painel",
    description="🪐 Central de gerenciamento de painéis de ticket"
)
@commands.has_permissions(administrator=True)
async def painel(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="🪐 Central de Gerenciamento de Painéis",
        description="Utilize o menu abaixo para gerenciar os painéis de ticket do servidor.",
        color=0x3e0b4d
    )
    embed.set_footer(text="Cosmos [Ticket] • Sistema estelar")
    
    view = MainMenuView()
    await inter.response.send_message(embed=embed, view=view, ephemeral=True)

# View do menu principal
class MainMenuView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @disnake.ui.string_select(
        placeholder="Selecione uma ação...",
        options=[
            disnake.SelectOption(label="Criar Painel", value="criar", emoji="➕"),
            disnake.SelectOption(label="Editar Painel", value="editar", emoji="✏️"),
            disnake.SelectOption(label="Remover Painel", value="remover", emoji="🗑️"),
            disnake.SelectOption(label="Listar Painéis", value="listar", emoji="📋")
        ]
    )
    async def menu_callback(self, select: disnake.ui.StringSelect, inter: disnake.MessageInteraction):
        action = select.values[0]
        
        if action == "criar":
            await self.criar_painel(inter)
        elif action == "editar":
            await self.editar_painel(inter)
        elif action == "remover":
            await self.remover_painel(inter)
        elif action == "listar":
            await self.listar_paineis(inter)
    
    async def criar_painel(self, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        guild_id = str(inter.guild.id)
        
        if guild_id not in paineis:
            paineis[guild_id] = {}
        
        # Gerar ID único
        panel_id = f"painel_{len(paineis[guild_id]) + 1}"
        paineis[guild_id][panel_id] = create_panel_structure(inter.guild.id, panel_id)
        save_data(DATABASE_FILE, paineis)
        
        view = PanelConfigView(panel_id)
        embed = view.get_config_embed(inter.guild.id, panel_id)
        await inter.response.edit_message(embed=embed, view=view)
    
    async def editar_painel(self, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        guild_id = str(inter.guild.id)
        
        if guild_id not in paineis or not paineis[guild_id]:
            await inter.response.send_message("❌ Nenhum painel encontrado!", ephemeral=True)
            return
        
        options = [
            disnake.SelectOption(label=pid, value=pid, emoji="📋")
            for pid in paineis[guild_id].keys()
        ]
        
        view = SelectPanelView(options, "editar")
        embed = disnake.Embed(
            title="✏️ Selecione um painel para editar",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    async def remover_painel(self, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        guild_id = str(inter.guild.id)
        
        if guild_id not in paineis or not paineis[guild_id]:
            await inter.response.send_message("❌ Nenhum painel encontrado!", ephemeral=True)
            return
        
        options = [
            disnake.SelectOption(label=pid, value=pid, emoji="🗑️")
            for pid in paineis[guild_id].keys()
        ]
        
        view = SelectPanelView(options, "remover")
        embed = disnake.Embed(
            title="🗑️ Selecione um painel para remover",
            color=0xff0000
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    async def listar_paineis(self, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        guild_id = str(inter.guild.id)
        
        if guild_id not in paineis or not paineis[guild_id]:
            embed = disnake.Embed(
                title="📋 Painéis do Servidor",
                description="Nenhum painel encontrado.",
                color=0x3e0b4d
            )
        else:
            description = ""
            for pid, data in paineis[guild_id].items():
                canal = f"<#{data['canal_id']}>" if data['canal_id'] else "Não definido"
                opcoes_count = len(data['opcoes'])
                description += f"\n**{pid}**\n├ Canal: {canal}\n├ Opções: {opcoes_count}\n└ Tipo: {data['tipo_exibicao'].title()}\n"
            
            embed = disnake.Embed(
                title="📋 Painéis do Servidor",
                description=description,
                color=0x3e0b4d
            )
        
        embed.set_footer(text="Cosmos [Ticket] • Sistema estelar")
        await inter.response.edit_message(embed=embed, view=MainMenuView())

# View para seleção de painel
class SelectPanelView(disnake.ui.View):
    def __init__(self, options: List[disnake.SelectOption], action: str):
        super().__init__(timeout=300)
        self.action = action
        
        select = disnake.ui.StringSelect(
            placeholder="Selecione um painel...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
        
        back_button = disnake.ui.Button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙")
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def select_callback(self, inter: disnake.MessageInteraction):
        panel_id = inter.values[0]
        
        if self.action == "editar":
            view = PanelConfigView(panel_id)
            embed = view.get_config_embed(inter.guild.id, panel_id)
            await inter.response.edit_message(embed=embed, view=view)
        elif self.action == "remover":
            paineis = load_data(DATABASE_FILE)
            guild_id = str(inter.guild.id)
            
            # Remover mensagem publicada se existir
            if paineis[guild_id][panel_id]['mensagem_id']:
                try:
                    canal = inter.guild.get_channel(paineis[guild_id][panel_id]['canal_id'])
                    if canal:
                        msg = await canal.fetch_message(paineis[guild_id][panel_id]['mensagem_id'])
                        await msg.delete()
                except:
                    pass
            
            del paineis[guild_id][panel_id]
            save_data(DATABASE_FILE, paineis)
            
            embed = disnake.Embed(
                title="✅ Painel Removido",
                description=f"O painel **{panel_id}** foi removido com sucesso!",
                color=0x00ff00
            )
            await inter.response.edit_message(embed=embed, view=MainMenuView())
    
    async def back_callback(self, inter: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="🪐 Central de Gerenciamento de Painéis",
            description="Utilize o menu abaixo para gerenciar os painéis de ticket do servidor.",
            color=0x3e0b4d
        )
        embed.set_footer(text="Cosmos [Ticket] • Sistema estelar")
        await inter.response.edit_message(embed=embed, view=MainMenuView())

if __name__ == "__main__":
    bot.run("token")
