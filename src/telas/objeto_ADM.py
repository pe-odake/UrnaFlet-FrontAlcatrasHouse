import flet as ft
import requests

API_URL = "http://192.168.0.66:8000/"

def build(page: ft.Page):
    page.clean()
    page.title = "Cadastro de Objeto"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    nome = ft.TextField(label="Nome do Objeto", width=300, border_color=ft.Colors.RED)
    descricao = ft.TextField(label="Descrição", multiline=True, width=300, border_color=ft.Colors.RED)
    msg = ft.Text(value="", color=ft.Colors.RED)
    foto_path = ft.Text(value="")

    imagem_visualizacao = ft.Image(src="", width=70, visible=False, border_radius=10)

    file_picker = ft.FilePicker()

    def selecionar_foto(e):
        file_picker.pick_files(allow_multiple=False)

    def voltar_para_tela_principal(e):
        page.go("/inicial_ADM")

    def foto_selecionada(e: ft.FilePickerResultEvent):
        if e.files:
            foto_path.value = e.files[0].path
            page.update()

    def cadastrar(e):
        if not foto_path.value:
            msg.value = "Selecione uma imagem."
            msg.color = ft.Colors.RED
            imagem_visualizacao.visible = False
            page.update()
            return

        with open(foto_path.value, "rb") as f:
            files = {"foto": f}
            data = {"nome": nome.value, "descricao": descricao.value}
            res = requests.post(f"{API_URL}/objeto", data=data, files=files)

        if res.status_code == 200:
            dados = res.json()
            objeto_id = dados.get("id")

            msg.value = (
                f"Objeto cadastrado com sucesso!\n"
                f"Nome: {dados.get('nome')}\n"
                f"Descrição: {dados.get('descricao')}"
            )
            msg.color = ft.Colors.GREEN

            imagem_visualizacao.src = f"{API_URL}imagem/{objeto_id}"
            imagem_visualizacao.visible = True
        else:
            msg.value = res.json().get("detail", "Erro ao cadastrar")
            msg.color = ft.Colors.RED
            imagem_visualizacao.visible = False

        page.update()

    file_picker.on_result = foto_selecionada
    page.overlay.append(file_picker)
    btn_voltar = ft.ElevatedButton(
        "Voltar",
        icon=ft.Icons.ARROW_BACK,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        on_click=voltar_para_tela_principal  # ajuste se necessário
    )
    return ft.View(
        route="/objetos",
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("Cadastro de Objeto", size=30, weight="bold", color=ft.Colors.RED),
                    nome,
                    descricao,
                    ft.ElevatedButton(
                        "Selecionar Foto",
                        on_click=selecionar_foto,
                        icon=ft.Icons.IMAGE,
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.WHITE
                    ),
                    foto_path,
                    ft.ElevatedButton(
                        "Cadastrar Objeto",
                        on_click=cadastrar,
                        icon=ft.Icons.CHECK,
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.WHITE
                    ),
                    msg,
                    imagem_visualizacao,
                    btn_voltar
                ],
                spacing=15,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=25,
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.RED),
                shadow=ft.BoxShadow(
                    blur_radius=6,
                    color=ft.Colors.RED_100,
                    offset=ft.Offset(2, 2)
                )
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
    )
