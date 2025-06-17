import flet as ft
import requests
from functools import partial
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

API_URL = "http://192.168.0.66:8000/"

def build(page: ft.Page):  # ← mudou de main() para build()
    page.title = "Sistema de Votação"
    page.theme_mode = ft.ThemeMode.LIGHT

    def ir_para_votacao(e, votacao_id: int):
        page.go(f"/votacao/{votacao_id}")
        
    def ir_para_resultados(e, votacao_id: int):
        page.go(f"/resultados/{votacao_id}")

    def carregar_view_lista_votacoes():
        res = requests.get(f"{API_URL}/votacoes")
        if res.status_code != 200:
            return ft.View("/", [ft.Text("Erro ao carregar votações")])

        votacoes = res.json()
        cards = []

        for v in votacoes:
            data_final = datetime.strptime(v["Data_final"], "%d/%m/%Y")
            encerrada = data_final < datetime.now() or v["Status_Votacao"] == 0
            texto_botao = "Ver Resultados" if encerrada else "Participar"
            texto_status = "Encerrada" if encerrada else "Ativa"
            rota_destino = ir_para_resultados if encerrada else ir_para_votacao
                                    
            cards.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text("Data de Encerramento", weight="bold"), ft.Text(v["Data_final"] or "dd/mm/yyyy")]),
                        ft.Column([ft.Text("Código", weight="bold"), ft.Text(str(v["ID_Votacao"]))]),
                        ft.Column([ft.Text("Assunto", weight="bold"), ft.Text(v["Tema"])]),
                        ft.Column([ft.Text("Status", weight="bold"), ft.Text(texto_status)]),
                        ft.Column([ft.Text("Participantes", weight="bold"), ft.Text("XX")]),  # substitua XX quando tiver os dados
                        ft.ElevatedButton(
                            texto_botao,
                            bgcolor=ft.Colors.RED,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=24, vertical=20)),
                            on_click=partial(rota_destino, votacao_id=v["ID_Votacao"])
                        )
                    ], alignment="spaceBetween"),
                    border=ft.border.all(2, ft.Colors.RED),
                    border_radius=10,
                    padding=10,
                    margin=5,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.Colors.RED_100,
                        offset=ft.Offset(2, 2)
                    )
                )
            )
            
        return ft.View(
            route="/ver_votacao",  # ← ESSENCIAL para funcionar como rota!
            controls=[
                ft.Text("Votações", size=30, weight="bold", color=ft.Colors.RED),
                *cards
            ],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def carregar_view_votacao(votacao_id: str):
        msg = ft.Text(value="", color=ft.Colors.RED)
        participantes_col = ft.Column(scroll=ft.ScrollMode.ALWAYS)
        imagem = ft.Image(
            src="../UrnaFlet-FrontEnd/imagemvoto.png",  # imagem padrão
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10
        )
        nome_selecionado = ft.Text(value="Nome", size=14, weight="bold", color=ft.Colors.WHITE)
        id_objeto_selecionado = ft.Text(value="", visible=False)

        voto_realizado = {"status": False}

        def selecionar_candidato(obj):
            imagem.src = f"{API_URL}/imagem/{obj['id']}"
            nome_selecionado.value = obj["nome"]
            id_objeto_selecionado.value = str(obj["id"])
            page.update()

        def confirmar_voto(e):
            if voto_realizado["status"]:
                msg.value = "Você já realizou seu voto nesta votação"
                msg.color = ft.Colors.RED
                msg.bgcolor= ft.Colors.WHITE
                page.update()
                return

            if not id_objeto_selecionado.value:
                msg.value = "Selecione um participante!"
                msg.color = ft.Colors.RED
                page.update()
                return

            try:
                res = requests.post(f"{API_URL}/adicionar_voto", json={
                    "id_votacao": votacao_id,
                    "id_eleitor": 1,  # Substituir pelo valor correto
                    "id_objeto_votacao": int(id_objeto_selecionado.value),
                })

                if res.status_code == 200:
                    msg.value = "Voto feito com sucesso!"
                    msg.color = ft.Colors.WHITE
                    voto_realizado["status"] = True
                else:
                    msg.value = res.json().get("mensagem", "Erro ao votar.")
                    msg.color = ft.Colors.RED
            except Exception as err:
                msg.value = f"Erro: {err}"
                msg.color = ft.Colors.RED
            page.update()

        try:
            res = requests.get(f"{API_URL}/objetos", params={"id_votacao": votacao_id})
            if res.status_code == 200:
                objetos = res.json()
                for obj in objetos:
                    participantes_col.controls.append(
                        ft.TextButton(
                            text=obj["nome"],
                            on_click=lambda e, obj=obj: selecionar_candidato(obj),
                            style=ft.ButtonStyle(
                                color=ft.Colors.RED,
                                padding=10,
                            )
                        )
                    )
        except Exception as e:
            print(f"Erro ao carregar objetos: {e}")

        return ft.View(
            route=f"/votacao/{votacao_id}",
            controls=[
                ft.Text("Vote", size=52, weight="bold", color=ft.Colors.RED),
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=350,
                            bgcolor=ft.Colors.WHITE,
                            border=ft.border.all(2, ft.Colors.RED),
                            border_radius=8,
                            padding=20,
                            content=ft.Column([
                                ft.Text("Lista de participantes", weight="bold", color=ft.Colors.RED, size=16),
                                ft.Divider(thickness=1, color=ft.Colors.RED),
                                participantes_col
                            ],
                            scroll=ft.ScrollMode.ALWAYS)
                        ),
                        ft.Container(
                            bgcolor=ft.Colors.RED,
                            expand=True,
                            border_radius=8,
                            padding=60,
                            content=ft.Column([
                                imagem,
                                nome_selecionado,
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "Confirmar",
                                    on_click=confirmar_voto,
                                    bgcolor=ft.Colors.WHITE,
                                    color=ft.Colors.RED,
                                    style=ft.ButtonStyle(padding=ft.Padding(20, 10, 20, 10))

                                ),
                                msg
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER)
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Voltar",
                    icon=ft.Icons.ARROW_BACK,
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: page.go("/ver_votacao")
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )


    def gerar_grafico_base64(resultados):
        nomes = [r["nome"] for r in resultados]
        votos = [r["total_votos"] for r in resultados]

        fig, ax = plt.subplots(figsize=(5, 4), facecolor='none')
        ax.pie(votos, labels=nomes, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        fig.patch.set_alpha(0.0)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', transparent=True)
        plt.close(fig)

        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
        
    def carregar_view_resultado(votacao_id: str):
        participantes_col = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)
        imagem = ft.Image(
            src="../UrnaFlet-FrontEnd/imagemvoto.png",  # imagem padrão
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10
        )
        
        nome_selecionado = ft.Text(
            value="Selecione um participante",
            size=20, weight="bold",
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER
        )
        grafico_img = ft.Image(width=360, height=360, border_radius=12)
        resultado_votacao = ft.Text(
            value="",
            size=22,
            weight="bold",
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER
        )
        erro_msg = ft.Text(value="", color=ft.Colors.RED)

        try:
            res = requests.get(f"{API_URL}/resultados", params={"id_votacao": votacao_id})
            if res.status_code == 200:
                resultados = res.json()

                for obj in resultados:
                    participantes_col.controls.append(
                        ft.Container(
                            content=ft.TextButton(
                                text=f"{obj['nome']} — {obj['total_votos']} voto(s)",
                                on_click=lambda e, obj=obj: (
                                    setattr(imagem, "src", f"{API_URL}/imagem/{obj['id']}"),
                                    setattr(nome_selecionado, "value", obj["nome"]),
                                    page.update()
                                ),
                                style=ft.ButtonStyle(
                                    padding=ft.Padding(12, 8, 12, 8),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    color=ft.Colors.BLACK87,
                                    bgcolor=ft.Colors.WHITE,
                                    overlay_color=ft.Colors.RED_100,
                                )
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.RED_100)),
                            padding=ft.Padding(5, 5, 5, 5)
                        )
                    )

                vencedor = max(resultados, key=lambda r: r['total_votos'])
                resultado_votacao.value = f"🏆 {vencedor['nome']} venceu com {vencedor['total_votos']} voto(s)"
                grafico_img.src_base64 = gerar_grafico_base64(resultados)
            else:
                erro_msg.value = "Erro ao carregar os resultados."
        except Exception as e:
            erro_msg.value = f"Erro: {e}"

        return ft.View(
            route=f"/resultados/{votacao_id}",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=30,
                    bgcolor=ft.Colors.RED_50,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=16,
                        spread_radius=1,
                        color=ft.Colors.RED_100,
                        offset=ft.Offset(3, 3)
                    ),
                    content=ft.Column([
                        ft.Text("📊 Resultado da Votação", size=34, weight="bold", color=ft.Colors.RED),
                        ft.Divider(height=25, color="transparent"),
                        ft.Row([
                            ft.Container(
                                width=360,
                                padding=20,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=12,
                                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.RED_100),
                                content=ft.Column([
                                    ft.Text("Participantes", size=22, weight="bold", color=ft.Colors.RED),
                                    ft.Divider(thickness=1, color=ft.Colors.RED),
                                    participantes_col
                                ])
                            ),
                            ft.Container(
                                expand=True,
                                padding=30,
                                bgcolor=ft.Colors.RED,
                                border_radius=12,
                                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.RED_200),
                                content=ft.Column([
                                    imagem,
                                    nome_selecionado,
                                    grafico_img,
                                    resultado_votacao
                                ],
                                spacing=25,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            " Voltar para Votações ",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: page.go("/ver_votacao"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                bgcolor=ft.Colors.RED_600,
                                color=ft.Colors.WHITE,
                                padding=ft.Padding(20, 14, 20, 14),
                            )
                        ),
                        erro_msg
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            ]
        )


    def route_change(e: ft.RouteChangeEvent):
        rota = e.route
        page.views.clear()

        if rota == "/ver_votacao":
            page.views.append(carregar_view_lista_votacoes())
        elif rota.startswith("/votacao/"):
            page.views.append(carregar_view_votacao(rota.split("/")[2]))
        elif rota.startswith("/resultados/"):
            page.views.append(carregar_view_resultado(rota.split("/")[2]))

        page.update()

    page.on_route_change = route_change
    return carregar_view_lista_votacoes()
    page.go(page.route or "/ver_votacao")
