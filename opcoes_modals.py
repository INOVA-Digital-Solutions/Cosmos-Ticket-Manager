import disnake
from disnake.ext import commands
import json
from typing import Dict
from views import *
from ticket_system import *
from opcoes_view import *
from modals import *
from config import *
def load_data(file: str) -> Dict:
    import os
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(file: str, data: Dict):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

DATABASE_FILE = "paineis.json"

# Modal para adicionar opção
class AdicionarOpcaoModal(disnake.ui.Modal):
    def __init__(self, panel_id: str):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Nome da Opção",
                placeholder="Ex: Suporte Técnico",
                custom_id="nome",
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Emoji",
                placeholder="Ex: 🔧 (opcional)",
                custom_id="emoji",
                required=False,
                max_length=10
            ),
            disnake.ui.TextInput(
                label="ID da Categoria (opcional)",
                placeholder="ID da categoria onde o ticket será criado",
                custom_id="categoria",
                required=False,
                max_length=20
            )
        ]
        super().__init__(title="Adicionar Opção", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        nome = inter.text_values['nome']
        emoji = inter.text_values.get('emoji', '📋').strip() or '📋'
        categoria_id = inter.text_values.get('categoria', '').strip()
        
        categoria = None
        if categoria_id:
            try:
                categoria = int(categoria_id)
                cat_obj = inter.guild.get_channel(categoria)
                if not cat_obj or not isinstance(cat_obj, disnake.CategoryChannel):
                    await inter.response.send_message("⚠️ Categoria inválida, usando padrão do painel.", ephemeral=True)
                    categoria = None
            except ValueError:
                await inter.response.send_message("⚠️ ID de categoria inválido, usando padrão do painel.", ephemeral=True)
                categoria = None
        
        nova_opcao = {
            'nome': nome,
            'emoji': emoji,
            'categoria_id': categoria
        }
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['opcoes'].append(nova_opcao)
        save_data(DATABASE_FILE, paineis)
        
        from opcoes_view import OpcoesView
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))
        await inter.followup.send(f"✅ Opção **{nome}** adicionada!", ephemeral=True)

# Modal para editar opção
class EditarOpcaoModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, index: int, opcao: Dict):
        self.panel_id = panel_id
        self.index = index
        components = [
            disnake.ui.TextInput(
                label="Nome da Opção",
                placeholder="Ex: Suporte Técnico",
                custom_id="nome",
                value=opcao['nome'],
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Emoji",
                placeholder="Ex: 🔧",
                custom_id="emoji",
                value=opcao.get('emoji', '📋'),
                max_length=10
            ),
            disnake.ui.TextInput(
                label="ID da Categoria (opcional)",
                placeholder="ID da categoria onde o ticket será criado",
                custom_id="categoria",
                value=str(opcao['categoria_id']) if opcao.get('categoria_id') else "",
                required=False,
                max_length=20
            )
        ]
        super().__init__(title="Editar Opção", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        nome = inter.text_values['nome']
        emoji = inter.text_values['emoji'].strip() or '📋'
        categoria_id = inter.text_values.get('categoria', '').strip()
        
        categoria = None
        if categoria_id:
            try:
                categoria = int(categoria_id)
                cat_obj = inter.guild.get_channel(categoria)
                if not cat_obj or not isinstance(cat_obj, disnake.CategoryChannel):
                    await inter.response.send_message("⚠️ Categoria inválida, usando padrão do painel.", ephemeral=True)
                    categoria = None
            except ValueError:
                await inter.response.send_message("⚠️ ID de categoria inválido, usando padrão do painel.", ephemeral=True)
                categoria = None
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['opcoes'][self.index] = {
            'nome': nome,
            'emoji': emoji,
            'categoria_id': categoria
        }
        save_data(DATABASE_FILE, paineis)
        
        from opcoes_view import OpcoesView
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))
        await inter.followup.send(f"✅ Opção **{nome}** editada!", ephemeral=True)

# Modal para mensagem de abertura
class MensagemAberturaModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, msg_atual: str):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Mensagem de Abertura",
                placeholder="Use {user} para mencionar o usuário",
                custom_id="mensagem",
                value=msg_atual,
                style=disnake.TextInputStyle.paragraph,
                max_length=2000
            )
        ]
        super().__init__(title="Mensagem de Abertura", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        mensagem = inter.text_values['mensagem']
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['mensagem_abertura'] = mensagem
        save_data(DATABASE_FILE, paineis)
        
        from opcoes_view import MensagensView
        view = MensagensView(self.panel_id)
        embed = disnake.Embed(
            title="✉️ Configurar Mensagens",
            description="Escolha qual mensagem deseja configurar:",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Mensagem de abertura atualizada!", ephemeral=True)

# Modal para mensagem de fechamento
class MensagemFechamentoModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, msg_atual: str):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Mensagem de Fechamento",
                placeholder="Use {user} para mencionar o usuário",
                custom_id="mensagem",
                value=msg_atual,
                style=disnake.TextInputStyle.paragraph,
                max_length=2000
            )
        ]
        super().__init__(title="Mensagem de Fechamento", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        mensagem = inter.text_values['mensagem']
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['mensagem_fechamento'] = mensagem
        save_data(DATABASE_FILE, paineis)
        
        from opcoes_view import MensagensView
        view = MensagensView(self.panel_id)
        embed = disnake.Embed(
            title="✉️ Configurar Mensagens",
            description="Escolha qual mensagem deseja configurar:",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Mensagem de fechamento atualizada!", ephemeral=True)
