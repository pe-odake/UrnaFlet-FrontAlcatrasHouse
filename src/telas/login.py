import flet as ft
import subprocess, time
import re
import json
import requests
import urllib.parse
import asyncio
# Imagem e link de confirmação
LOGO_URL = "https://lh3.googleusercontent.com/chat_attachment/AP1Ws4vVUU-_RiAddakivrHdPYOfPlkue8vpmmpiekOqFJHLXHw04W9ubKgF9dOzpIve1YLvgvWQbyE7TWsNppU6lPSSM6b3dlk57eUNmKJWA3Ej2NJjSZKZ3mDOO7x-3UTsLpcM6KNbGzbwNaoO69CJ16IEPq5ufOPkkdaAsJs43W3S-f--oUh3-sRkMgNeBEwhs-y-lXP89UDFTHUPcpjUL3KSq8K8Vl8IMyE1m0qa2T7qn9f8eeOsQhpigyHoUByziDmVkc9CddqCuTP4ESrvYEw6pasfl-GlmH6b4RZ2ccWh5f2CevkMAK2oFJSw5WLF3aQ=w512"
CONFIRM_URL = "http://192.168.0.66:8000/confirmar?email="

API_URL = "http://192.168.0.66:8000/"

SMTP2GO_API_KEY = "api-250A06463CE94D1B8D229463C101927A"
REMETENTE_EMAIL = "guilherme.p.silva20@aluno.senai.br"
REMETENTE_NOME = "Sistema de Votação"

# def start_server():
#     subprocess.Popen(["python", "servidor.py"])

def build(page: ft.Page):
    page.title = "Login"
    page.bgcolor = ft.Colors.WHITE
    # page.window.full_screen = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    def enviar_email(email: str, existente: bool):
        encoded_email = urllib.parse.quote(email)

        if existente:
            conteudo = f"""
            <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;padding:30px;text-align:center;color:#333;">
                <div style="max-width:600px;margin:auto;background-color:#ffffff;padding:30px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);">
                    <img src="{LOGO_URL}" alt="Logo Votus" style="width:120px;margin-bottom:20px;border-radius:8px"/>
                    <h1 style="color:#FF585B;">Bem-vindo de volta à Votus!</h1>
                    <p style="font-size:16px;margin:20px 0;">
                        Identificamos que você já possui uma conta em nossa plataforma.
                        Deseja continuar com sua votação?
                    </p>
                    <a href="{CONFIRM_URL + encoded_email}" style="display:inline-block;margin:10px;padding:12px 24px;background-color:#FF585B;color:white;text-decoration:none;border-radius:5px;font-weight:bold;">
                        Sim, continuar votação
                    </a>
                    <a href="#" style="display:inline-block;margin:10px;padding:12px 24px;background-color:#cccccc;color:#333;text-decoration:none;border-radius:5px;">
                        Não, obrigado
                    </a>
                    <hr style="margin:40px 0;border:none;border-top:1px solid #eee"/>
                    <p style="font-size:14px;color:#666;">
                        A <strong>Votus</strong> é a plataforma mais segura e moderna para suas votações. 
                        Privacidade, praticidade e confiança em cada clique. 🔒
                    </p>
                    <p style="font-size:13px;color:#aaa;">© 2025 Votus. Todos os direitos reservados.</p>
                </div>
            </div>
            """
        else:
            conteudo = f"""
            <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;padding:30px;text-align:center;color:#333;">
                <div style="max-width:600px;margin:auto;background-color:#ffffff;padding:30px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);">
                    <img src="{LOGO_URL}" alt="Logo Votus" style="width:120px;margin-bottom:20px;border-radius:8px"/>
                    <h1 style="color:#FF585B;">Seja bem-vindo à Votus!</h1>
                    <p style="font-size:16px;margin:20px 0;">
                        Percebemos que você ainda não tem uma conta em nossa plataforma.
                        Gostaria de se cadastrar agora e participar da votação?
                    </p>
                    <a href="{CONFIRM_URL + encoded_email}" style="display:inline-block;margin:10px;padding:12px 24px;background-color:#FF585B;color:white;text-decoration:none;border-radius:5px;font-weight:bold;">
                        Sim, quero me cadastrar
                    </a>
                    <a href="#" style="display:inline-block;margin:10px;padding:12px 24px;background-color:#cccccc;color:#333;text-decoration:none;border-radius:5px;">
                        Não, obrigado
                    </a>
                    <hr style="margin:40px 0;border:none;border-top:1px solid #eee"/>
                    <p style="font-size:14px;color:#666;">
                        Descubra como a <strong>Votus</strong> revoluciona a forma de votar. 
                        Simples, intuitivo e totalmente online. Comece agora! 🗳️
                    </p>
                    <p style="font-size:13px;color:#aaa;">© 2025 Votus. Todos os direitos reservados.</p>
                </div>
            </div>
            """
            

        payload = {
            "api_key": SMTP2GO_API_KEY,
            "to": [email],
            "sender": REMETENTE_EMAIL,
            "subject": "Verificação de Conta",
            "html_body": conteudo,
            "text_body": "Verifique sua conta no site.",
            "custom_headers": [{"header": "Reply-To", "value": REMETENTE_EMAIL}]
        }

        response = requests.post(
            "https://api.smtp2go.com/v3/email/send",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        print("Status:", response.status_code)
        print("Resposta:", response.text)
        return response.status_code == 200

    # FUNÇÃO QUE ADD EMIAL NO BANCO DE DADOS
    def registrar(e):
        res = requests.post(f"{API_URL}/register", json={
            "email": email_field.value,
            #'nome': email_field.value
        })
        print(email_field.value)
        if res.status_code == 200:
            print('Email adicionado com sucesso')
        else:
            print('Email não adicionado')
        page.update()


    email_field = ft.TextField(
        hint_text="Digite o seu email",
        border_color="#FF585B",
        bgcolor="#FFDEDE",
        color="#FF585B",
        width=300,
    )

    # # CAMPO PARA POR O NOME

    # nome_field = ft.TextField(
    #     hint_text="Digite seu nome",
    #     border_color="#FF585B",
    #     bgcolor="#FFDEDE",
    #     color="#FF585B",
    #     width=300,
    #     visible=False  # inicialmente escondido
    # )

    # status_text = ft.Text("", color=ft.Colors.RED)

    # ja_cadastrado_global = False  # variável para controlar estado

    # #FIM

    status_text = ft.Text("", color=ft.Colors.RED)

    async def verificar_email(e):
        email = email_field.value.strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            status_text.value = "Email inválido."
            page.update()
            return

        try:
            response = requests.post(f"{API_URL}/verificar-email", json={"email": email})
            response.raise_for_status()
            ja_cadastrado = response.json().get("existe", False)
        except Exception as ex:
            status_text.value = f"Erro ao verificar email: {ex}"
            page.update()
            return
        
        # if not ja_cadastrado:
        #     # Se não cadastrado, mostra campo nome para o usuário preencher
        #     nome_field.visible = True
        #     status_text.value = "Email não cadastrado. Por favor, informe seu nome para cadastro."
        #     page.update()
        #     return  # para o fluxo aqui, espera o usuário preencher nome e clicar no botão novamente
        
        # # Se cadastrado, continua o processo normal
        # nome_field.visible = False
        # page.update()

        try:
            requests.post(f"{API_URL}/registrar-token", json={"email": email})
        except Exception as ex:
            status_text.value = f"Erro ao registrar token: {ex}"
            page.update()
            return

        if not ja_cadastrado:
            registrar(e)

        sucesso = enviar_email(email, ja_cadastrado)

        if sucesso:
            status_text.value = "Email enviado! Verifique sua caixa de entrada..."
            page.update()

            for _ in range(60):
                await asyncio.sleep(3)
                try:
                    r = requests.get(f"{API_URL}/confirmado", params={"email": email})
                    if r.status_code == 200 and r.json().get("confirmado"):
                        status_text.value = "✅ Email confirmado! Acesso liberado."
                        page.session.set("usuario_logado", email)
                        print("Email existente no Banco de Dados")
                        page.update()

                        # NOVA VERIFICAÇÃO: Se é administrador
                        try:
                            admin_res = requests.post(f"{API_URL}/verificar-administrador", json={"email": email})
                            if admin_res.status_code == 200 and admin_res.json().get("administrador"):
                                page.go("/inicial_ADM")
                            else:
                                page.go("/ver_votacao")
                        except Exception as ex:
                            status_text.value = f"Erro ao redirecionar: {ex}"
                            page.update()
                        return
                except:
                    pass
            status_text.value = "⏳ Tempo esgotado para confirmação."
            page.update()
        else:
            status_text.value = "Erro ao enviar o email. Veja o terminal."
            page.update()

    # def registrar_com_nome(e):
    #     email = email_field.value.strip()
    #     nome = nome_field.value.strip()

    #     if not nome:
    #         status_text.value = "Por favor, informe seu nome para cadastro."
    #         page.update()
    #         return

    #     res = requests.post(f"{API_URL}/register", json={
    #         "email": email,
    #         "nome": nome
    #     })
    #     if res.status_code == 200:
    #         status_text.value = "Cadastro realizado com sucesso! Agora, verifique seu email."
    #         page.update()
    #         # Depois do cadastro, pode enviar o email de confirmação:
    #         enviar_email(email, False)
    #     else:
    #         status_text.value = "Erro ao cadastrar. Tente novamente."
    #         page.update()

    # # O botão deve chamar verificar_email se o nome_field está invisível,
    # # ou registrar_com_nome se o nome_field está visível
    # def on_login_click(e):
    #     if nome_field.visible:
    #         registrar_com_nome(e)
    #     else:
    #         # chamar a função async verificacao via create_task
    #         asyncio.create_task(verificar_email(e))
        
    esquerda = ft.Container(
        content=ft.Column([
            ft.Text("Possui uma conta ?", size=50, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(
                "Ei, se você ainda não tem uma conta por aqui! Que tal aproveitar e \n"
                "se juntar ao melhor site de votações da internet? É rapidinho, grátis e você\n"
                " ainda participa das decisões mais importantes com apenas alguns cliques. \n"
                "Não fique de fora dessa — insira o seu e email no campo ao lado, verifique \n"
                "a sua caixa de SPAM e comece a votar com estilo!",
                size=12,
                color=ft.Colors.WHITE,
            ),
            ft.Text("OBS: O email pode demorar alguns segundos para chegar em seu correio!", size=20, color=ft.Colors.WHITE,weight=ft.FontWeight.W_600),
            ft.Image(src="../UrnaFlet-FrontEnd/image1.png", width=600)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=40),
        bgcolor="#FF585B",
        expand=True,
        padding=200
    )

    direita = ft.Container(
        content=ft.Column([
            ft.Text("Login", size=24, weight=ft.FontWeight.BOLD, color="#FF585B"),
            email_field,
            # nome_field,
            ft.ElevatedButton(
                "Login",
                bgcolor="#FF585B",
                color="white",
                on_click=verificar_email,
                width=300
            ),
            status_text
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20),
        expand=True
    )

    layout = ft.Row(
        controls=[esquerda, direita],
        expand=True
    )

    return ft.View(
        route="/",
        controls=[layout],  # O layout final que você montou
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

#rodar codigo com: uvicorn main:app --host 0.0.0.0 --port 8000 --reload