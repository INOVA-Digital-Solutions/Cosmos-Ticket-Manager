import disnake
from disnake.ext import commands
import json
from typing import Dict
from views import *
from ticket_system import *
from modals import *
from opcoes_modals import *
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

# View para gerenciar opções
class OpcoesView(disnake.ui.View):
    def __init__(self, panel_id: str):
        super().__init__(timeout=600)
        self.panel_id = panel_id
        self.update_select_options()
    
    def update_select_options(self):
        # Limpar items antigos (exceto botões fixos)
        items_to_remove = [item for item in self.children if isinstance(item, disnake.ui.StringSelect)]
        for item in items_to_remove:
            self.remove_item(item)
    
    @disnake.ui.button(label="Adicionar Opção", style=disnake.ButtonStyle.success, emoji="➕", row=0)
    async def adicionar_opcao(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        modal = AdicionarOpcaoModal(self.panel_id)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Editar Opção", style=disnake.ButtonStyle.primary, emoji="✏️", row=0)
    async def editar_opcao(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        opcoes = paineis[str(inter.guild.id)][self.panel_id]['opcoes']
        
        if not opcoes:
            await inter.response.send_message("❌ Nenhuma opção para editar!", ephemeral=True)
            return
        
        select_options = [
            disnake.SelectOption(
                label=opt['nome'][:100],
                value=str(i),
                emoji=opt.get('emoji', '📋')
            ) for i, opt in enumerate(opcoes)
        ]
        
        view = SelectOpcaoEditView(self.panel_id, select_options)
        embed = disnake.Embed(
            title="✏️ Selecione uma opção para editar",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Remover Opção", style=disnake.ButtonStyle.danger, emoji="❌", row=1)
    async def remover_opcao(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        opcoes = paineis[str(inter.guild.id)][self.panel_id]['opcoes']
        
        if not opcoes:
            await inter.response.send_message("❌ Nenhuma opção para remover!", ephemeral=True)
            return
        
        select_options = [
            disnake.SelectOption(
                label=opt['nome'][:100],
                value=str(i),
                emoji=opt.get('emoji', '📋')
            ) for i, opt in enumerate(opcoes)
        ]
        
        view = SelectOpcaoRemoveView(self.panel_id, select_options)
        embed = disnake.Embed(
            title="🗑️ Selecione uma opção para remover",
            color=0xff0000
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Tipo de Exibição", style=disnake.ButtonStyle.primary, emoji="🔁", row=1)
    async def tipo_exibicao(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        tipo_atual = paineis[str(inter.guild.id)][self.panel_id]['tipo_exibicao']
        
        view = TipoExibicaoView(self.panel_id, tipo_atual)
        embed = disnake.Embed(
            title="🔁 Tipo de Exibição",
            description=f"**Tipo Atual:** {tipo_atual.title()}\n\nEscolha como as opções serão exibidas:",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙", row=2)
    async def voltar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from views import PanelConfigView
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        await inter.response.edit_message(embed=embed, view=view)

# View para tipo de exibição
class TipoExibicaoView(disnake.ui.View):
    def __init__(self, panel_id: str, tipo_atual: str):
        super().__init__(timeout=300)
        self.panel_id = panel_id
        
        select = disnake.ui.StringSelect(
            placeholder=f"Atual: {tipo_atual.title()}",
            options=[
                disnake.SelectOption(label="Dropdown", value="dropdown", emoji="📋", description="Menu suspenso"),
                disnake.SelectOption(label="Botões", value="botoes", emoji="🔘", description="Botões clicáveis")
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)
        
        back_button = disnake.ui.Button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙")
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def select_callback(self, inter: disnake.MessageInteraction):
        tipo = inter.values[0]
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['tipo_exibicao'] = tipo
        save_data(DATABASE_FILE, paineis)
        
        embed = disnake.Embed(
            title="✅ Tipo Atualizado",
            description=f"Tipo de exibição alterado para: **{tipo.title()}**",
            color=0x00ff00
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))
    
    async def back_callback(self, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=OpcoesView(self.panel_id))

# View para selecionar opção para editar
class SelectOpcaoEditView(disnake.ui.View):
    def __init__(self, panel_id: str, options):
        super().__init__(timeout=300)
        self.panel_id = panel_id
        
        select = disnake.ui.StringSelect(
            placeholder="Selecione uma opção...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
        
        back_button = disnake.ui.Button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙")
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def select_callback(self, inter: disnake.MessageInteraction):
        index = int(inter.component.values[0])
        paineis = load_data(DATABASE_FILE)
        opcao = paineis[str(inter.guild.id)][self.panel_id]['opcoes'][index]
        
        modal = EditarOpcaoModal(self.panel_id, index, opcao)
        await inter.response.send_modal(modal)
    
    async def back_callback(self, inter: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))

# View para selecionar opção para remover
class SelectOpcaoRemoveView(disnake.ui.View):
    def __init__(self, panel_id: str, options):
        super().__init__(timeout=300)
        self.panel_id = panel_id
        
        select = disnake.ui.StringSelect(
            placeholder="Selecione uma opção...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
        
        back_button = disnake.ui.Button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙")
        back_button.callback = self.back_callback
        self.add_item(back_button)
    
    async def select_callback(self, inter: disnake.MessageInteraction):
        index = int(inter.component.values[0])
        paineis = load_data(DATABASE_FILE)
        opcao = paineis[str(inter.guild.id)][self.panel_id]['opcoes'][index]
        
        view = ConfirmarRemocaoView(self.panel_id, index, opcao['nome'])
        embed = disnake.Embed(
            title="⚠️ Confirmar Remoção",
            description=f"Tem certeza que deseja remover a opção **{opcao['nome']}**?",
            color=0xff0000
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    async def back_callback(self, inter: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))

# View para confirmar remoção
class ConfirmarRemocaoView(disnake.ui.View):
    def __init__(self, panel_id: str, index: int, nome: str):
        super().__init__(timeout=300)
        self.panel_id = panel_id
        self.index = index
        self.nome = nome
    
    @disnake.ui.button(label="Confirmar", style=disnake.ButtonStyle.danger, emoji="✅")
    async def confirmar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['opcoes'].pop(self.index)
        save_data(DATABASE_FILE, paineis)
        
        embed = disnake.Embed(
            title="✅ Opção Removida",
            description=f"A opção **{self.nome}** foi removida com sucesso!",
            color=0x00ff00
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))
    
    @disnake.ui.button(label="Cancelar", style=disnake.ButtonStyle.gray, emoji="❌")
    async def cancelar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=OpcoesView(self.panel_id))

# View para mensagens
class MensagensView(disnake.ui.View):
    def __init__(self, panel_id: str):
        super().__init__(timeout=600)
        self.panel_id = panel_id
    
    @disnake.ui.button(label="Mensagem de Abertura", style=disnake.ButtonStyle.primary, emoji="📩", row=0)
    async def msg_abertura(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        msg_atual = paineis[str(inter.guild.id)][self.panel_id]['mensagem_abertura']
        modal = MensagemAberturaModal(self.panel_id, msg_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Mensagem de Fechamento", style=disnake.ButtonStyle.primary, emoji="📪", row=0)
    async def msg_fechamento(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        msg_atual = paineis[str(inter.guild.id)][self.panel_id]['mensagem_fechamento']
        modal = MensagemFechamentoModal(self.panel_id, msg_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙", row=1)
    async def voltar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from views import PanelConfigView
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        await inter.response.edit_message(embed=embed, view=view)
