import flet as ft
import requests

API_URL = "http://192.168.0.66:8000/"

def build(page: ft.Page):
    page.clean()
    page.title = "Eleitores por Votação"
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    selected_votacao = {"ID_Votacao": None, "Nome": ""}

    titulo = ft.Text("Gerenciar Eleitores por Votação", size=32, weight="bold", color=ft.Colors.RED)
    subtitulo = ft.Text("Selecione uma votação abaixo para visualizar e atribuir eleitores.", size=16, italic=True)
    msg = ft.Text(value="", color=ft.Colors.RED)

    botoes_votacoes = ft.Column(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    botoes_eleitores = ft.Column(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

    def adicionar_eleitor(eleitor_id):
        if not selected_votacao["ID_Votacao"]:
            msg.value = "Selecione uma votação primeiro."
            msg.color = ft.Colors.RED
            page.update()
            return

        try:
            res = requests.post(f"{API_URL}/addEleitorVotacao", json={
                "id_votacao": selected_votacao["ID_Votacao"],
                "id_eleitor": eleitor_id,
                "valido": 1
            })
            if res.status_code == 200:
                msg.value = f"Eleitor {eleitor_id} adicionado com sucesso!"
                msg.color = ft.Colors.GREEN
            else:
                msg.value = res.json().get("detail", "Erro ao adicionar eleitor.")
                msg.color = ft.Colors.RED
        except Exception as err:
            msg.value = f"Erro: {err}"
            msg.color = ft.Colors.RED
        page.update()

    def voltar_para_tela_principal(e):
        page.go("/inicial_ADM")

    def carregar_eleitores():
        botoes_eleitores.controls.clear()
        try:
            res = requests.get(f"{API_URL}/eleitores")
            if res.status_code == 200:
                eleitores = res.json()
                for eleitor in eleitores:
                    botoes_eleitores.controls.append(
                        ft.Container(
                            content=ft.ElevatedButton(
                                text=eleitor["nome"],
                                bgcolor=ft.Colors.WHITE,
                                color=ft.Colors.RED,
                                on_click=lambda e, eid=eleitor["id"]: adicionar_eleitor(eid),
                                style=ft.ButtonStyle(padding=20, shape=ft.RoundedRectangleBorder(radius=10))
                            ),
                            padding=5
                        )
                    )
            else:
                botoes_eleitores.controls.append(ft.Text("Erro ao buscar eleitores."))
        except Exception as e:
            botoes_eleitores.controls.append(ft.Text(f"Erro: {e}"))
        page.update()

    def selecionar_votacao(votacao):
        selected_votacao["ID_Votacao"] = votacao["ID_Votacao"]
        selected_votacao["Nome"] = votacao["Nome"]
        msg.value = f"Votação selecionada: {votacao['Nome']}"
        msg.color = ft.Colors.RED
        carregar_eleitores()
        page.update()

    def carregar_votacoes():
        botoes_votacoes.controls.clear()
        try:
            res = requests.get(f"{API_URL}/votacoes")
            if res.status_code == 200:
                votacoes = res.json()
                for votacao in votacoes:
                    botoes_votacoes.controls.append(
                        ft.Container(
                            content=ft.ElevatedButton(
                                text=f"{votacao['Nome']} - {votacao['Tema']}",
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE,
                                on_click=lambda e, v=votacao: selecionar_votacao(v),
                                style=ft.ButtonStyle(padding=20, shape=ft.RoundedRectangleBorder(radius=10))
                            ),
                            padding=5
                        )
                    )
            else:
                botoes_votacoes.controls.append(ft.Text("Erro ao carregar votações."))
        except Exception as e:
            botoes_votacoes.controls.append(ft.Text(f"Erro ao buscar votações: {e}"))
        page.update()

    altura_container = 350
    btn_voltar = ft.ElevatedButton(
        "Voltar",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=voltar_para_tela_principal
    )

    layout = ft.Column([
        titulo,
        subtitulo,
        ft.Divider(height=20, color="transparent"),
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Votações", size=22, weight="bold", color=ft.Colors.RED),
                    botoes_votacoes
                ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.RED),
                border_radius=10,
                padding=20,
                expand=True,
                height=altura_container,
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.RED_100)
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Eleitores", size=22, weight="bold", color=ft.Colors.WHITE),
                    botoes_eleitores
                ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.RED,
                border=ft.border.all(2, ft.Colors.WHITE),
                border_radius=10,
                padding=20,
                expand=True,
                height=altura_container,
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.RED_100)
            )
        ], spacing=30, alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=20, color="transparent"),
        msg,
        btn_voltar
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    carregar_votacoes()

    return ft.View(
        route="/eleitor-votacao",
        controls=[layout],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
