import flet as ft
import requests
from datetime import datetime
import subprocess
import sys
import os

API_URL = "http://192.168.0.66:8000/"

def build(page: ft.Page):
    usuario_logado = page.session.get("usuario_logado")
    print("Usuário logado:", usuario_logado)
    

    page.clean()
    page.title = "Gerenciar Votações"
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    nome = ft.TextField(label="Nome", width=300, border_color=ft.Colors.RED)
    tema = ft.TextField(label="Tema", width=300, border_color=ft.Colors.RED)
    data_info = None
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    data_encerramento_txt = ft.Text("Data de encerramento não selecionada", size=14, color=ft.Colors.RED)
    msg = ft.Text(value="", color=ft.Colors.RED)
    msgSucess = ft.Text(value="", color=ft.Colors.GREEN)
    

        
        
    # Date Picker
    def on_date_change(e):
        nonlocal data_info
        data_info = e.control.value
        data_encerramento_txt.value = f"Encerramento: {data_info.strftime('%d/%m/%Y')}"
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2000, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(date_picker)

    btn_data = ft.ElevatedButton(
        "Selecionar Data de Encerramento",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: page.open(date_picker),
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE
    )

    def AddVotacao(e):
        if not all([nome.value, tema.value, data_info]):
            msg.value = "Preencha todos os campos e selecione uma data."
            msg.color = ft.Colors.RED
        else:
            try:
                res = requests.post(f"{API_URL}/addVotacao", json={
                    "nome": nome.value,
                    "tema": tema.value,
                    "data_hoje": data_hoje,
                    "data_encerramento": data_info.strftime("%d/%m/%Y")
                })
                if res.status_code == 200:
                    msgSucess.value = "Votação adicionada com sucesso!"
                    msgSucess.color = ft.Colors.GREEN
                    nome.value = tema.value = ""
                    data_encerramento_txt.value = "Data de encerramento não selecionada"
                else:
                    msgSucess.value = res.json().get("detail", "Erro ao adicionar")
                    msgSucess.color = ft.Colors.RED
            except Exception as err:
                msgSucess.value = f"Erro na requisição: {err}"
                msgSucess.color = ft.Colors.RED
        page.update()

    btn_add = ft.ElevatedButton("Adicionar Votação", icon=ft.Icons.ADD, on_click=AddVotacao, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)

    # Encerrar por tema
    temas_dropdown = ft.Dropdown(
        label="Encerrar votação pelo tema",
        width=300,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.WHITE,
        color=ft.Colors.WHITE,
        
    )

    def carregar_temas():
        try:
            res = requests.get(f"{API_URL}/votacoes")
            if res.status_code == 200:
                votacoes = res.json()
                temas_dropdown.options = [
                    ft.dropdown.Option(v["Tema"]) for v in votacoes if v["Tema"]
                ]
        except Exception as e:
            msg.value = f"Erro ao carregar temas: {e}"
        page.update()
        
    def voltar_para_tela_principal(e):
        page.go("/") 

    def ir_para_add_objetovotacao(e):
        page.go("/objeto-votacao")

    def ir_para_cadastrar_objeto(e):
        page.go("/objetos")

    def ir_para_add_eleitorvotacao(e):
        page.go("/eleitor-votacao")

    def encerrar_votacao_por_tema(e):
        tema_escolhido = temas_dropdown.value
        if not tema_escolhido:
            msg.value = "Selecione um tema para encerrar."
            msg.color = ft.Colors.WHITE
            page.update()
            return

        try:
            res = requests.get(f"{API_URL}/votacoes")
            if res.status_code == 200:
                votacoes = res.json()
                votacao = next((v for v in votacoes if v["Tema"] == tema_escolhido), None)
                if votacao:
                    encerrar_res = requests.post(f"{API_URL}/encerrarVotacao", json={"id_votacao": votacao["ID_Votacao"]})
                    if encerrar_res.status_code == 200:
                        msg.value = f"Votação '{tema_escolhido}' encerrada com sucesso!"
                        msg.color = ft.Colors.WHITE
                    else:
                        msg.value = encerrar_res.json().get("detail", "Erro ao encerrar votação")
                        msg.color = ft.Colors.WHITE
        except Exception as err:
            msg.value = f"Erro na requisição: {err}"
            msg.color = ft.Colors.WHITE

        page.update()

    btn_encerrar = ft.ElevatedButton("Confirmar  ", icon=ft.Icons.CLOSE, on_click=encerrar_votacao_por_tema, bgcolor=ft.Colors.WHITE, color=ft.Colors.RED)

    carregar_temas()

    # Layout
    altura_container = 360

    esquerda = ft.Container(
        content=ft.Column([
            ft.Text(" Criar Votação ", size=30, weight="bold",color=ft.Colors.RED),
            nome,
            tema,
            btn_data,
            data_encerramento_txt,
            btn_add,
            msgSucess
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.RED),
        height=altura_container,
        expand=1,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.RED_100,
            offset=ft.Offset(2, 2)
        )        
    )

    direita = ft.Container(
        content=ft.Column([
            ft.Text("Encerrar Votação \n", size=30, weight="bold", color=ft.Colors.WHITE),
            temas_dropdown,
            btn_encerrar,
            msg
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.RED,
        height=altura_container,
        expand=1,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=18,
            color=ft.Colors.RED_100,
            offset=ft.Offset(3, 2)
        )         
    )

    btn_add_objetovotacao = ft.ElevatedButton(
        "Adicionar Objeto a Votação",
        icon=ft.Icons.LIST_ALT,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=ir_para_add_objetovotacao
    )
    btn_add_eleitorvotacao = ft.ElevatedButton(
        "Adicionar Eleitor a Votação",
        icon=ft.Icons.LIST_ALT,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=ir_para_add_eleitorvotacao
    )

    btn_objetos = ft.ElevatedButton(
        "Cadastrar Objeto",
        icon=ft.Icons.ADD_BOX,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=ir_para_cadastrar_objeto
    )

    btn_voltar = ft.ElevatedButton(
        "Sair do perfil Administrador",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=voltar_para_tela_principal  # ajuste se necessário
    )

    return ft.View(
        route="/inicial_ADM",
        controls=[
            ft.Column(
                [
                    ft.Row(
                        [esquerda, direita],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        [btn_add_eleitorvotacao,btn_add_objetovotacao, btn_objetos],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Divider(height=10, color="transparent"),
                    btn_voltar
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )



