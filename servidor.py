from flask import Flask, request, render_template
import socket
import threading
import os
import subprocess

app = Flask(__name__)
clientes = []

def manejar_cliente(cliente_socket, direccion):
    global clientes
    print(f"Conexión establecida desde {direccion}")
    clientes.append(cliente_socket)

    try:
        while True:
            mensaje = cliente_socket.recv(1024).decode()
            if not mensaje:
                break
            print(f"[{direccion}] {mensaje}")

            # Responder a comandos específicos
            if mensaje.startswith("chat:"):
                for cliente in clientes:
                    if cliente != cliente_socket:
                        cliente.sendall(f"Mensaje de {direccion}: {mensaje[5:]}".encode())
            elif mensaje == "captura":
                capturar_pantalla(cliente_socket)
            elif mensaje == "bloquear":
                bloquear_teclado_y_mouse()
                cliente_socket.sendall("Teclado y mouse bloqueados.".encode())
            elif mensaje == "desbloquear":
                desbloquear_teclado_y_mouse()
                cliente_socket.sendall("Teclado y mouse desbloqueados.".encode())
            elif mensaje == "apagar":
                apagar_pc()
                cliente_socket.sendall("El PC se apagará.".encode())
            elif mensaje.startswith("bloquear_web:"):
                dominio = mensaje.split(":")[1]
                bloquear_pagina_web(dominio)
                cliente_socket.sendall(f"Acceso a {dominio} bloqueado.".encode())
            elif mensaje == "permitir_ping":
                permitir_ping()
                cliente_socket.sendall("Ping permitido.".encode())
            elif mensaje == "denegar_ping":
                denegar_ping()
                cliente_socket.sendall("Ping denegado.".encode())
    except:
        pass
    finally:
        print(f"Conexión cerrada con {direccion}")
        clientes.remove(cliente_socket)
        cliente_socket.close()

def capturar_pantalla(cliente_socket):
    try:
        os.system('scrot captura.png')
        with open('captura.png', 'rb') as f:
            cliente_socket.sendall(f.read())
        os.remove('captura.png')
    except Exception as e:
        cliente_socket.sendall(f"Error al capturar pantalla: {str(e)}".encode())

def bloquear_teclado_y_mouse():
    os.system("xinput --disable $(xinput | grep -i 'keyboard' | grep -Po 'id=\\d+' | cut -d= -f2)")
    os.system("xinput --disable $(xinput | grep -i 'mouse' | grep -Po 'id=\\d+' | cut -d= -f2)")

def desbloquear_teclado_y_mouse():
    os.system("xinput --enable $(xinput | grep -i 'keyboard' | grep -Po 'id=\\d+' | cut -d= -f2)")
    os.system("xinput --enable $(xinput | grep -i 'mouse' | grep -Po 'id=\\d+' | cut -d= -f2)")

def apagar_pc():
    os.system("shutdown now")

def bloquear_pagina_web(dominio):
    with open("/etc/hosts", "a") as hosts_file:
        hosts_file.write(f"127.0.0.1 {dominio}\n")

def permitir_ping():
    os.system("sudo iptables -D INPUT -p icmp --icmp-type echo-request -j DROP")

def denegar_ping():
    os.system("sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar_comando', methods=['POST'])
def enviar_comando():
    datos = request.json
    comando = datos.get('comando', '')

    if comando:
        # Aquí puedes manejar los comandos recibidos
        return f"Comando recibido: {comando}"
    return "No se recibió ningún comando", 400

def iniciar_servidor_socket(host='0.0.0.0', puerto=9999):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, puerto))
    servidor.listen(5)
    print(f"Servidor socket escuchando en {host}:{puerto}")

    while True:
        cliente_socket, direccion = servidor.accept()
        hilo_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
        hilo_cliente.start()

if __name__ == '__main__':
    threading.Thread(target=iniciar_servidor_socket).start()
    app.run(host='0.0.0.0', port=5000)
