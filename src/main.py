import flet as ft
from telas import inicial_ADM, objeto_ADM, objeto_votacao_ADM,eleitor_votacao, login,ver_votacao

def main(page: ft.Page):

    def route_change(e):
        page.views.clear()
        page.window.full_screen = True

        if page.route == "/":
            page.views.append(login.build(page))
        elif page.route == "/objetos":
            page.views.append(objeto_ADM.build(page))
        elif page.route == "/eleitor-votacao":
            page.views.append(eleitor_votacao.build(page))
        elif page.route == "/objeto-votacao":
            page.views.append(objeto_votacao_ADM.build(page))
        elif page.route == "/login":
            page.views.append(login.build(page))
        elif page.route == "/inicial_ADM":
            page.views.append(inicial_ADM.build(page))# NOVA ROTA
        elif page.route == "/ver_votacao":
            page.views.append(ver_votacao.build(page))            
        page.update()
    page.on_route_change = route_change
    page.go(page.route or "/")  # abre a rota atual ou padrão "/"

ft.app(target=main)
