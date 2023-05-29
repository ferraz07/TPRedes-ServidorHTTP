#servidor
 
import socket
import threading
import os
import platform
import datetime
import getpass


HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(3)
print(f"Server escutando na porta: {PORT}")

clients = []
usernames = []

def sendMessage(message):
    for cliente in clients:
        cliente.send(message)


def sendListaArq(client):
    file_list = os.listdir()
    file_list_show = '\n'.join(file_list)
    client.send(f"Lista de arquivos no servidor:\n{file_list_show}\n".encode('utf-8'))

def handle(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('sendfile'):
                filename = message.split(' ')[1]
                sendFile(client, filename)
            elif message.startswith('getfile'):
                sendListaArq(client)
            elif message.startswith('/HEADER'):
                header = message.split('\r\n\r\n')[0]
                sendHeader(client, header) 
            elif message.startswith('/INFO'):
                sendInfo(client)
            elif message.startswith('/HELLO'):
                hello(client,username)
            else:
                sendMessage(f"[{username}] {message}".encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            usernames.remove(username)
            sendMessage(f"{username} se desconectou do servidor.".encode('utf-8'))
            break

def sendFile(client, filename):
    if os.path.isfile(filename):
        client.send(f"Enviando arquivo {filename}...\n".encode('utf-8'))
        with open(filename, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client.send(data)
        client.send("\nArquivo enviado com sucesso!\n".encode('utf-8'))
    else:
        client.send(f"\nArquivo {filename} não encontrado.\n".encode('utf-8'))

def sendHeader(client,header):
    client.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{header}\n".encode('utf-8'))

def hello(client, username):
    client.send(f"Olá {username}, sou um servidor!\n".encode('utf-8'))

def sendInfo(client):
    so = platform.platform()
    data = datetime.datetime.now().strftime('%Y-%m-%d ---- %H:%M')
    usuario = getpass.getuser()

    message = f"Sistema operacional: {so}\nData: {data}\nNome do usuário: {usuario}\n"
    client.send(message.encode('utf-8'))

def receive():
    while True:
        client, address = tcp.accept()
        client.send("USERNAME".encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
 
        print(f"O usuário {username} se conectou no servidor! endereço: {address}")
        sendMessage(f"{username} entrou no chat.".encode('utf-8'))
        clients.append(client)
        client.send('\nConectado ao servidor!\n'.encode('utf-8'))
        client.send("\nPara receber a lista de arquivos do servidor, digite 'getfile'\nPara enviar um arquivo, digite 'sendfile + nome_do_arquivo'\nPara receber o header HTTP, digite '/HEADER'\nPara receber as informações sobre o computador, digite '/INFO'\n\n".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client, username, ))
        thread.start()


receive()
