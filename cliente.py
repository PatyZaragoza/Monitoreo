
import socket
import os
import pyautogui
import platform
import subprocess
import threading
import time

def escuchar_servidor(cliente_socket):
    try:
        while True:
            comando = cliente_socket.recv(1024).decode()
            if not comando:
                break
            ejecutar_comando_local(comando)
    except:
        print("Conexión perdida con el servidor.")
    finally:
        cliente_socket.close()

def enviar_datos(cliente_socket):
    while True:
        mensaje = input("Introduce el mensaje o comando: ")
        cliente_socket.sendall(mensaje.encode())

def ejecutar_comando_local(comando):
    if comando == "bloquear":
        # Bloquear teclado y mouse
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(0, 0)
        print("Teclado y mouse bloqueados.")
    elif comando == "desbloquear":
        # Desbloquear teclado y mouse
        pyautogui.FAILSAFE = True
        print("Teclado y mouse desbloqueados.")
    elif comando == "apagar":
        # Apagar la máquina
        if platform.system() == "Linux":
            os.system("shutdown now")
        elif platform.system() == "Windows":
            os.system("shutdown /s /t 0")
        print("Apagando el sistema...")
    elif comando == "captura":
        # Tomar una captura de pantalla y enviarla al servidor
        captura = pyautogui.screenshot()
        captura.save("captura.png")
        print("Captura de pantalla realizada.")
    elif comando.startswith("bloquear_web:"):
        # Bloquear acceso a una web usando iptables (solo en Linux)
        dominio = comando.split(":")[1]
        os.system(f"sudo iptables -A OUTPUT -p tcp --dport 80 -d {dominio} -j REJECT")
        print(f"Acceso bloqueado a {dominio}")
    elif comando == "permitir_ping":
        # Permitir ping (ICMP) usando iptables
        os.system("sudo iptables -D INPUT -p icmp --icmp-type echo-request -j DROP")
        print("Ping permitido.")
    elif comando == "denegar_ping":
        # Denegar ping (ICMP) usando iptables
        os.system("sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP")
        print("Ping denegado.")
    else:
        print("Comando no reconocido.")

def iniciar_cliente(host='127.0.0.1', puerto=9999):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, puerto))

    hilo_escuchar = threading.Thread(target=escuchar_servidor, args=(cliente,))
    hilo_escuchar.start()

    enviar_datos(cliente)

if __name__ == '_main_':
    iniciar_cliente()