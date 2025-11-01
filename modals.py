import disnake
from disnake.ext import commands
import json
from typing import Dict, Optional
from views import *
from ticket_system import *
from opcoes_view import *

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

# Modal para alterar canal
class AlterarCanalModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, canal_atual: Optional[int]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="ID do Canal",
                placeholder="Insira o ID do canal",
                custom_id="canal_id",
                value=str(canal_atual) if canal_atual else "",
                max_length=20
            )
        ]
        super().__init__(title="Alterar Canal", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        canal_id = inter.text_values['canal_id']
        
        try:
            canal_id = int(canal_id)
            canal = inter.guild.get_channel(canal_id)
            
            if not canal:
                await inter.response.send_message("❌ Canal não encontrado!", ephemeral=True)
                return
            
            if not canal.permissions_for(inter.guild.me).send_messages:
                await inter.response.send_message("❌ Bot sem permissão para enviar mensagens neste canal!", ephemeral=True)
                return
            
            paineis = load_data(DATABASE_FILE)
            paineis[str(inter.guild.id)][self.panel_id]['canal_id'] = canal_id
            save_data(DATABASE_FILE, paineis)
            
            from views import PanelConfigView
            view = PanelConfigView(self.panel_id)
            embed = view.get_config_embed(inter.guild.id, self.panel_id)
            
            await inter.response.edit_message(embed=embed, view=view)
            await inter.followup.send(f"✅ Canal alterado para {canal.mention}", ephemeral=True)
        except ValueError:
            await inter.response.send_message("❌ ID inválido!", ephemeral=True)

# Modal para gerenciar permissões (cargo de suporte)
class GerenciarPermissoesModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, cargo_atual: Optional[int]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="ID do Cargo de Suporte",
                placeholder="Insira o ID do cargo (deixe vazio para remover)",
                custom_id="cargo_id",
                value=str(cargo_atual) if cargo_atual else "",
                max_length=20,
                required=False
            )
        ]
        super().__init__(title="Gerenciar Permissões", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        cargo_id = inter.text_values['cargo_id'].strip()
        
        paineis = load_data(DATABASE_FILE)
        
        if not cargo_id:
            paineis[str(inter.guild.id)][self.panel_id]['cargo_suporte_id'] = None
            save_data(DATABASE_FILE, paineis)
        else:
            try:
                cargo_id = int(cargo_id)
                cargo = inter.guild.get_role(cargo_id)
                
                if not cargo:
                    await inter.response.send_message("❌ Cargo não encontrado!", ephemeral=True)
                    return
                
                paineis[str(inter.guild.id)][self.panel_id]['cargo_suporte_id'] = cargo_id
                save_data(DATABASE_FILE, paineis)
            except ValueError:
                await inter.response.send_message("❌ ID inválido!", ephemeral=True)
                return
        
        from views import PanelConfigView
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Permissões atualizadas!", ephemeral=True)

# Modal para gerenciar categoria
class GerenciarCategoriaModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, categoria_atual: Optional[int]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="ID da Categoria",
                placeholder="Insira o ID da categoria de tickets",
                custom_id="categoria_id",
                value=str(categoria_atual) if categoria_atual else "",
                max_length=20,
                required=False
            )
        ]
        super().__init__(title="Gerenciar Categoria", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        categoria_id = inter.text_values['categoria_id'].strip()
        
        paineis = load_data(DATABASE_FILE)
        
        if not categoria_id:
            paineis[str(inter.guild.id)][self.panel_id]['categoria_id'] = None
            save_data(DATABASE_FILE, paineis)
        else:
            try:
                categoria_id = int(categoria_id)
                categoria = inter.guild.get_channel(categoria_id)
                
                if not categoria or not isinstance(categoria, disnake.CategoryChannel):
                    await inter.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
                    return
                
                paineis[str(inter.guild.id)][self.panel_id]['categoria_id'] = categoria_id
                save_data(DATABASE_FILE, paineis)
            except ValueError:
                await inter.response.send_message("❌ ID inválido!", ephemeral=True)
                return
        
        from views import PanelConfigView
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Categoria atualizada!", ephemeral=True)

# Modal para configurar logs
class ConfigurarLogsModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, log_atual: Optional[int]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="ID do Canal de Logs",
                placeholder="Insira o ID do canal de logs (vazio para remover)",
                custom_id="log_id",
                value=str(log_atual) if log_atual else "",
                max_length=20,
                required=False
            )
        ]
        super().__init__(title="Configurar Logs", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        log_id = inter.text_values['log_id'].strip()
        
        paineis = load_data(DATABASE_FILE)
        
        if not log_id:
            paineis[str(inter.guild.id)][self.panel_id]['log_canal_id'] = None
            save_data(DATABASE_FILE, paineis)
        else:
            try:
                log_id = int(log_id)
                canal = inter.guild.get_channel(log_id)
                
                if not canal:
                    await inter.response.send_message("❌ Canal não encontrado!", ephemeral=True)
                    return
                
                paineis[str(inter.guild.id)][self.panel_id]['log_canal_id'] = log_id
                save_data(DATABASE_FILE, paineis)
            except ValueError:
                await inter.response.send_message("❌ ID inválido!", ephemeral=True)
                return
        
        from views import PanelConfigView
        view = PanelConfigView(self.panel_id)
        embed = view.get_config_embed(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Logs configurados!", ephemeral=True)

# Modals de edição de embed
class EditarTituloModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, titulo_atual: str):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Título da Embed",
                placeholder="Digite o novo título",
                custom_id="titulo",
                value=titulo_atual,
                max_length=256
            )
        ]
        super().__init__(title="Alterar Título", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        titulo = inter.text_values['titulo']
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['titulo'] = titulo
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Título atualizado!", ephemeral=True)

class EditarDescricaoModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, desc_atual: str):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Descrição da Embed",
                placeholder="Digite a nova descrição",
                custom_id="descricao",
                value=desc_atual,
                style=disnake.TextInputStyle.paragraph,
                max_length=4000
            )
        ]
        super().__init__(title="Alterar Descrição", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        descricao = inter.text_values['descricao']
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['descricao'] = descricao
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Descrição atualizada!", ephemeral=True)

class EditarImagemModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, img_atual: Optional[str]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="URL da Imagem",
                placeholder="Cole a URL da imagem (vazio para remover)",
                custom_id="imagem",
                value=img_atual if img_atual else "",
                required=False,
                max_length=500
            )
        ]
        super().__init__(title="Alterar Imagem", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        imagem = inter.text_values['imagem'].strip()
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['imagem'] = imagem if imagem else None
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Imagem atualizada!", ephemeral=True)

class EditarThumbnailModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, thumb_atual: Optional[str]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="URL da Thumbnail",
                placeholder="Cole a URL da thumbnail (vazio para remover)",
                custom_id="thumbnail",
                value=thumb_atual if thumb_atual else "",
                required=False,
                max_length=500
            )
        ]
        super().__init__(title="Alterar Thumbnail", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        thumbnail = inter.text_values['thumbnail'].strip()
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['thumbnail'] = thumbnail if thumbnail else None
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Thumbnail atualizada!", ephemeral=True)

class EditarAutorModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, autor_atual: Optional[str]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Autor da Embed",
                placeholder="Digite o nome do autor (vazio para remover)",
                custom_id="autor",
                value=autor_atual if autor_atual else "",
                required=False,
                max_length=256
            )
        ]
        super().__init__(title="Alterar Autor", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        autor = inter.text_values['autor'].strip()
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['autor'] = autor if autor else None
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Autor atualizado!", ephemeral=True)

class EditarFooterModal(disnake.ui.Modal):
    def __init__(self, panel_id: str, footer_atual: Optional[str]):
        self.panel_id = panel_id
        components = [
            disnake.ui.TextInput(
                label="Footer da Embed",
                placeholder="Digite o footer (vazio para remover)",
                custom_id="footer",
                value=footer_atual if footer_atual else "",
                required=False,
                max_length=2048
            )
        ]
        super().__init__(title="Alterar Footer", components=components)
    
    async def callback(self, inter: disnake.ModalInteraction):
        footer = inter.text_values['footer'].strip()
        
        paineis = load_data(DATABASE_FILE)
        paineis[str(inter.guild.id)][self.panel_id]['embed']['footer'] = footer if footer else None
        save_data(DATABASE_FILE, paineis)
        
        from views import EditEmbedView
        view = EditEmbedView(self.panel_id)
        embed = view.get_embed_preview(inter.guild.id, self.panel_id)
        
        await inter.response.edit_message(embed=embed, view=view)
        await inter.followup.send("✅ Footer atualizado!", ephemeral=True)
