import disnake
from disnake.ext import commands
import json
import datetime
from typing import Dict, List
from views import *
from opcoes_view import *
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
TICKETS_FILE = "tickets.json"

# View com Dropdown para seleção de opção
class TicketDropdownView(disnake.ui.View):
    def __init__(self, panel_id: str, opcoes: List[Dict]):
        super().__init__(timeout=None)
        self.panel_id = panel_id
        
        select_options = [
            disnake.SelectOption(
                label=opt['nome'],
                value=f"{panel_id}_{i}",
                emoji=opt.get('emoji', '📋')
            ) for i, opt in enumerate(opcoes)
        ]
        
        select = disnake.ui.StringSelect(
            placeholder="Selecione uma opção...",
            options=select_options,
            custom_id=f"ticket_select_{panel_id}"
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, inter: disnake.MessageInteraction):
        await criar_ticket(inter, inter.values[0])

# View com Botões para seleção de opção
class TicketButtonView(disnake.ui.View):
    def __init__(self, panel_id: str, opcoes: List[Dict]):
        super().__init__(timeout=None)
        self.panel_id = panel_id
        
        for i, opt in enumerate(opcoes[:25]):  # Discord limita a 25 botões
            button = disnake.ui.Button(
                label=opt['nome'],
                style=disnake.ButtonStyle.primary,
                emoji=opt.get('emoji', '📋'),
                custom_id=f"ticket_btn_{panel_id}_{i}"
            )
            button.callback = lambda inter, idx=i: self.button_callback(inter, idx)
            self.add_item(button)
    
    async def button_callback(self, inter: disnake.MessageInteraction, index: int):
        await criar_ticket(inter, f"{self.panel_id}_{index}")

# Função principal para criar ticket
async def criar_ticket(inter: disnake.MessageInteraction, valor: str):
    panel_id, opcao_index = valor.rsplit('_', 1)
    opcao_index = int(opcao_index)
    
    paineis = load_data(DATABASE_FILE)
    tickets = load_data(TICKETS_FILE)
    
    guild_id = str(inter.guild.id)
    user_id = str(inter.user.id)
    
    # Verificar se usuário já tem ticket aberto
    if guild_id in tickets:
        for ticket_id, ticket_data in tickets[guild_id].items():
            if ticket_data['user_id'] == user_id and ticket_data['status'] == 'aberto':
                canal = inter.guild.get_channel(ticket_data['canal_id'])
                if canal:
                    await inter.response.send_message(
                        f"❌ Você já possui um ticket aberto: {canal.mention}",
                        ephemeral=True
                    )
                    return
    
    painel_data = paineis[guild_id][panel_id]
    opcao = painel_data['opcoes'][opcao_index]
    
    # Determinar categoria
    categoria_id = opcao.get('categoria_id') or painel_data.get('categoria_id')
    categoria = inter.guild.get_channel(categoria_id) if categoria_id else None
    
    # Criar canal de ticket
    ticket_nome = f"ticket-{inter.user.name}-{inter.user.discriminator}"
    
    overwrites = {
        inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
        inter.user: disnake.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True
        ),
        inter.guild.me: disnake.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            manage_messages=True
        )
    }
    
    # Adicionar cargo de suporte se existir
    if painel_data.get('cargo_suporte_id'):
        cargo = inter.guild.get_role(painel_data['cargo_suporte_id'])
        if cargo:
            overwrites[cargo] = disnake.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
    
    try:
        canal_ticket = await inter.guild.create_text_channel(
            name=ticket_nome,
            category=categoria,
            overwrites=overwrites,
            topic=f"Ticket de {inter.user.name} - {opcao['nome']}"
        )
    except Exception as e:
        await inter.response.send_message(
            f"❌ Erro ao criar ticket: {str(e)}",
            ephemeral=True
        )
        return
    
    # Salvar ticket no banco
    if guild_id not in tickets:
        tickets[guild_id] = {}
    
    ticket_id = f"ticket_{len(tickets[guild_id]) + 1}"
    tickets[guild_id][ticket_id] = {
        'canal_id': canal_ticket.id,
        'user_id': user_id,
        'panel_id': panel_id,
        'opcao': opcao['nome'],
        'status': 'aberto',
        'criado_em': datetime.datetime.now().isoformat(),
        'mensagens': []
    }
    save_data(TICKETS_FILE, tickets)
    
    # Enviar mensagem de abertura
    mensagem_abertura = painel_data['mensagem_abertura'].replace('{user}', inter.user.mention)
    
    embed = disnake.Embed(
        title=f"🎫 {opcao['nome']}",
        description=mensagem_abertura,
        color=0x3e0b4d,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Criado por", value=inter.user.mention, inline=True)
    embed.add_field(name="Opção", value=opcao['nome'], inline=True)
    embed.set_footer(text=f"Ticket ID: {ticket_id}")
    
    view = TicketControlView(ticket_id, panel_id)
    await canal_ticket.send(embed=embed, view=view)
    
    # Log
    if painel_data.get('log_canal_id'):
        log_canal = inter.guild.get_channel(painel_data['log_canal_id'])
        if log_canal:
            log_embed = disnake.Embed(
                title="📋 Novo Ticket Criado",
                description=f"**Usuário:** {inter.user.mention}\n"
                           f"**Canal:** {canal_ticket.mention}\n"
                           f"**Opção:** {opcao['nome']}\n"
                           f"**ID:** {ticket_id}",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            await log_canal.send(embed=log_embed)
    
    await inter.response.send_message(
        f"✅ Ticket criado com sucesso! {canal_ticket.mention}",
        ephemeral=True
    )

# View de controle do ticket
class TicketControlView(disnake.ui.View):
    def __init__(self, ticket_id: str, panel_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.panel_id = panel_id
    
    @disnake.ui.button(label="Fechar Ticket", style=disnake.ButtonStyle.danger, emoji="🔒", custom_id="fechar_ticket")
    async def fechar_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        tickets = load_data(TICKETS_FILE)
        paineis = load_data(DATABASE_FILE)
        
        guild_id = str(inter.guild.id)
        ticket_data = tickets[guild_id][self.ticket_id]
        painel_data = paineis[guild_id][self.panel_id]
        
        # Verificar permissão
        if str(inter.user.id) != ticket_data['user_id']:
            cargo_suporte = painel_data.get('cargo_suporte_id')
            if not cargo_suporte or cargo_suporte not in [r.id for r in inter.user.roles]:
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message(
                        "❌ Você não tem permissão para fechar este ticket!",
                        ephemeral=True
                    )
                    return
        
        # Confirmar fechamento
        view = ConfirmarFechamentoView(self.ticket_id, self.panel_id)
        embed = disnake.Embed(
            title="⚠️ Confirmar Fechamento",
            description="Tem certeza que deseja fechar este ticket?",
            color=0xff0000
        )
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @disnake.ui.button(label="Adicionar Membro", style=disnake.ButtonStyle.primary, emoji="➕", custom_id="add_membro")
    async def adicionar_membro(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        tickets = load_data(TICKETS_FILE)
        guild_id = str(inter.guild.id)
        ticket_data = tickets[guild_id][self.ticket_id]
        
        # Verificar permissão
        if str(inter.user.id) != ticket_data['user_id'] and not inter.user.guild_permissions.manage_channels:
            await inter.response.send_message(
                "❌ Você não tem permissão para adicionar membros!",
                ephemeral=True
            )
            return
        
        modal = AdicionarMembroModal(self.ticket_id)
        await inter.response.send_modal(modal)

# View para confirmar fechamento
class ConfirmarFechamentoView(disnake.ui.View):
    def __init__(self, ticket_id: str, panel_id: str):
        super().__init__(timeout=60)
        self.ticket_id = ticket_id
        self.panel_id = panel_id
    
    @disnake.ui.button(label="Confirmar", style=disnake.ButtonStyle.danger, emoji="✅")
    async def confirmar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        tickets = load_data(TICKETS_FILE)
        paineis = load_data(DATABASE_FILE)
        
        guild_id = str(inter.guild.id)
        ticket_data = tickets[guild_id][self.ticket_id]
        painel_data = paineis[guild_id][self.panel_id]
        
        # Atualizar status
        ticket_data['status'] = 'fechado'
        ticket_data['fechado_em'] = datetime.datetime.now().isoformat()
        ticket_data['fechado_por'] = str(inter.user.id)
        save_data(TICKETS_FILE, tickets)
        
        # Mensagem de fechamento
        mensagem_fechamento = painel_data['mensagem_fechamento'].replace('{user}', inter.user.mention)
        
        embed = disnake.Embed(
            title="🔒 Ticket Fechado",
            description=mensagem_fechamento,
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Fechado por {inter.user.name}")
        
        canal = inter.channel
        await canal.send(embed=embed)
        
        # Log
        if painel_data.get('log_canal_id'):
            log_canal = inter.guild.get_channel(painel_data['log_canal_id'])
            if log_canal:
                log_embed = disnake.Embed(
                    title="🔒 Ticket Fechado",
                    description=f"**Canal:** {canal.mention}\n"
                               f"**Fechado por:** {inter.user.mention}\n"
                               f"**ID:** {self.ticket_id}",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                await log_canal.send(embed=log_embed)
        
        await inter.response.edit_message(content="✅ Ticket sendo fechado...", embed=None, view=None)
        
        # Deletar canal após 5 segundos
        import asyncio
        await asyncio.sleep(5)
        await canal.delete(reason=f"Ticket fechado por {inter.user.name}")
    
    @disnake.ui.button(label="Cancelar", style=disnake.ButtonStyle.gray, emoji="❌")
    async def cancelar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(content="❌ Fechamento cancelado.", embed=None, view=None)

# Modal para adicionar membro
class AdicionarMembroModal(disnake.ui.Modal):
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        components = [
            disnake.ui.TextInput(
                label="ID do Usuário",
                placeholder="Insira o ID do usuário",
                custom_id="user_id",
                max_length=20
            )
        ]
        super().__init__(title="Adicionar Membro", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        user_id = inter.text_values['user_id']
        
        try:
            user_id = int(user_id)
            member = inter.guild.get_member(user_id)
            
            if not member:
                await inter.response.send_message("❌ Usuário não encontrado!", ephemeral=True)
                return
            
            await inter.channel.set_permissions(
                member,
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            
            await inter.response.send_message(
                f"✅ {member.mention} foi adicionado ao ticket!",
                ephemeral=False
            )
        except ValueError:
            await inter.response.send_message("❌ ID inválido!", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)
