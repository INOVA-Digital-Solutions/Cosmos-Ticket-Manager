import disnake
from disnake.ext import commands
import json
from typing import Dict, Optional
from ticket_system import *
from opcoes_view import *
from modals import *
from opcoes_modals import *
from config import *
# Importar funções de carregamento/salvamento
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

# View principal de configuração do painel
class PanelConfigView(disnake.ui.View):
    def __init__(self, panel_id: str):
        super().__init__(timeout=600)
        self.panel_id = panel_id
    
    def get_config_embed(self, guild_id: int, panel_id: str) -> disnake.Embed:
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(guild_id)][panel_id]
        
        canal = f"<#{data['canal_id']}>" if data['canal_id'] else "❌ Não definido"
        categoria = f"<#{data['categoria_id']}>" if data['categoria_id'] else "❌ Não definido"
        cargo = f"<@&{data['cargo_suporte_id']}>" if data['cargo_suporte_id'] else "❌ Não definido"
        log = f"<#{data['log_canal_id']}>" if data['log_canal_id'] else "❌ Não definido"
        opcoes = f"{len(data['opcoes'])} opção(ões)" if data['opcoes'] else "❌ Nenhuma opção"
        
        embed = disnake.Embed(
            title="🛠 Painel de Configuração",
            description=f"**Painel:** `{panel_id}`\n\n"
                       f"**Canal de Envio:** {canal}\n"
                       f"**Categoria de Tickets:** {categoria}\n"
                       f"**Cargo de Suporte:** {cargo}\n"
                       f"**Canal de Logs:** {log}\n"
                       f"**Opções Configuradas:** {opcoes}\n"
                       f"**Tipo de Exibição:** {data['tipo_exibicao'].title()}",
            color=0x3e0b4d
        )
        embed.set_footer(text="Cosmos [Ticket] • Configure seu painel")
        return embed
    
    @disnake.ui.button(label="Alterar Canal", style=disnake.ButtonStyle.primary, emoji="🖊️", row=0)
    async def alterar_canal(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(inter.guild.id)][self.panel_id]
        
        modal = AlterarCanalModal(self.panel_id, data['canal_id'])
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Editar Embed", style=disnake.ButtonStyle.primary, emoji="📄", row=0)
    async def editar_embed(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Gerenciar Permissões", style=disnake.ButtonStyle.primary, emoji="🔒", row=0)
    async def gerenciar_permissoes(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(inter.guild.id)][self.panel_id]
        
        modal = GerenciarPermissoesModal(self.panel_id, data['cargo_suporte_id'])
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Gerenciar Categoria", style=disnake.ButtonStyle.primary, emoji="📂", row=1)
    async def gerenciar_categoria(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(inter.guild.id)][self.panel_id]
        
        modal = GerenciarCategoriaModal(self.panel_id, data['categoria_id'])
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Mensagens", style=disnake.ButtonStyle.primary, emoji="✉️", row=1)
    async def alterar_mensagens(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = MensagensView(self.panel_id)
        embed = disnake.Embed(
            title="✉️ Configurar Mensagens",
            description="Escolha qual mensagem deseja configurar:",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Configurar Logs", style=disnake.ButtonStyle.primary, emoji="📜", row=1)
    async def configurar_logs(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(inter.guild.id)][self.panel_id]
        
        modal = ConfigurarLogsModal(self.panel_id, data['log_canal_id'])
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Opções", style=disnake.ButtonStyle.primary, emoji="⚙️", row=2)
    async def alterar_opcoes(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = OpcoesView(self.panel_id)
        embed = disnake.Embed(
            title="⚙️ Gerenciamento de Opções",
            description="Gerencie as opções do seu painel de ticket.",
            color=0x3e0b4d
        )
        await inter.response.edit_message(embed=embed, view=view)
    
    @disnake.ui.button(label="Enviar", style=disnake.ButtonStyle.success, emoji="🚀", row=2)
    async def enviar_painel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        data = paineis[str(inter.guild.id)][self.panel_id]
        
        # Validações
        erros = []
        if not data['canal_id']:
            erros.append("❌ Canal não definido")
        if not data['opcoes']:
            erros.append("❌ Nenhuma opção configurada")
        if not data['embed']['titulo'] or not data['embed']['descricao']:
            erros.append("❌ Embed incompleta (título e descrição obrigatórios)")
        
        if erros:
            embed = disnake.Embed(
                title="⚠️ Validação Falhou",
                description="\n".join(erros),
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verificar permissões
        canal = inter.guild.get_channel(data['canal_id'])
        if not canal:
            await inter.response.send_message("❌ Canal não encontrado!", ephemeral=True)
            return
        
        perms = canal.permissions_for(inter.guild.me)
        if not (perms.send_messages and perms.embed_links):
            await inter.response.send_message("❌ Bot sem permissões necessárias no canal!", ephemeral=True)
            return
        
        # Criar embed final
        embed_data = data['embed']
        embed = disnake.Embed(
            title=embed_data['titulo'],
            description=embed_data['descricao'],
            color=embed_data['cor']
        )
        
        if embed_data['imagem']:
            embed.set_image(url=embed_data['imagem'])
        if embed_data['thumbnail']:
            embed.set_thumbnail(url=embed_data['thumbnail'])
        if embed_data['autor']:
            embed.set_author(name=embed_data['autor'])
        if embed_data['footer']:
            embed.set_footer(text=embed_data['footer'])
        
        # Criar view de acordo com tipo de exibição
        if data['tipo_exibicao'] == 'dropdown':
            view = TicketDropdownView(self.panel_id, data['opcoes'])
        else:
            view = TicketButtonView(self.panel_id, data['opcoes'])
        
        # Remover mensagem anterior se existir
        if data['mensagem_id']:
            try:
                msg_antiga = await canal.fetch_message(data['mensagem_id'])
                await msg_antiga.delete()
            except:
                pass
        
        # Enviar nova mensagem
        mensagem = await canal.send(embed=embed, view=view)
        
        # Atualizar banco
        data['mensagem_id'] = mensagem.id
        save_data(DATABASE_FILE, paineis)
        
        # Confirmação
        conf_embed = disnake.Embed(
            title="✅ Painel Publicado",
            description=f"Painel publicado com sucesso em {canal.mention}\n"
                       f"**Tipo de exibição:** {data['tipo_exibicao'].title()}",
            color=0x00ff00
        )
        await inter.response.send_message(embed=conf_embed, ephemeral=True)
    
    @disnake.ui.button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙", row=2)
    async def voltar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from main import MainMenuView
        embed = disnake.Embed(
            title="🪐 Central de Gerenciamento de Painéis",
            description="Utilize o menu abaixo para gerenciar os painéis de ticket do servidor.",
            color=0x3e0b4d
        )
        embed.set_footer(text="Cosmos [Ticket] • Sistema estelar")
        await inter.response.edit_message(embed=embed, view=MainMenuView())

# View para edição de embed
class EditEmbedView(disnake.ui.View):
    def __init__(self, panel_id: str):
        super().__init__(timeout=600)
        self.panel_id = panel_id
    
    def get_embed_preview(self, guild_id: int, panel_id: str) -> disnake.Embed:
        paineis = load_data(DATABASE_FILE)
        embed_data = paineis[str(guild_id)][panel_id]['embed']
        
        embed = disnake.Embed(
            title="🖌 Painel de Edição da Embed",
            description="**📋 Pré-visualização:**",
            color=0x3e0b4d
        )
        
        preview = f"**Título:** {embed_data['titulo']}\n"
        preview += f"**Descrição:** {embed_data['descricao'][:100]}{'...' if len(embed_data['descricao']) > 100 else ''}\n"
        preview += f"**Cor:** #{hex(embed_data['cor'])[2:].zfill(6)}\n"
        preview += f"**Imagem:** {'✅ Definida' if embed_data['imagem'] else '❌ Não definida'}\n"
        preview += f"**Thumbnail:** {'✅ Definida' if embed_data['thumbnail'] else '❌ Não definida'}\n"
        preview += f"**Autor:** {embed_data['autor'] if embed_data['autor'] else '❌ Não definido'}\n"
        preview += f"**Footer:** {embed_data['footer'] if embed_data['footer'] else '❌ Não definido'}"
        
        embed.add_field(name="Configurações Atuais", value=preview, inline=False)
        embed.set_footer(text="Cosmos [Ticket] • Editor de Embed")
        return embed
    
    @disnake.ui.button(label="Alterar Título", style=disnake.ButtonStyle.primary, emoji="📝", row=0)
    async def alterar_titulo(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        titulo_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['titulo']
        modal = EditarTituloModal(self.panel_id, titulo_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Descrição", style=disnake.ButtonStyle.primary, emoji="📄", row=0)
    async def alterar_descricao(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        desc_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['descricao']
        modal = EditarDescricaoModal(self.panel_id, desc_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Imagem", style=disnake.ButtonStyle.primary, emoji="🖼️", row=1)
    async def alterar_imagem(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        img_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['imagem']
        modal = EditarImagemModal(self.panel_id, img_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Thumbnail", style=disnake.ButtonStyle.primary, emoji="🖼️", row=1)
    async def alterar_thumbnail(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        thumb_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['thumbnail']
        modal = EditarThumbnailModal(self.panel_id, thumb_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Autor", style=disnake.ButtonStyle.primary, emoji="👤", row=2)
    async def alterar_autor(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        autor_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['autor']
        modal = EditarAutorModal(self.panel_id, autor_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Alterar Footer", style=disnake.ButtonStyle.primary, emoji="🦶", row=2)
    async def alterar_footer(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        paineis = load_data(DATABASE_FILE)
        footer_atual = paineis[str(inter.guild.id)][self.panel_id]['embed']['footer']
        modal = EditarFooterModal(self.panel_id, footer_atual)
        await inter.response.send_modal(modal)
    
    @disnake.ui.button(label="Voltar", style=disnake.ButtonStyle.gray, emoji="🔙", row=3)
    async def voltar(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        await inter.response.edit_message(embed=embed, view=view)
