import socket
import threading
import os
import platform
import datetime
import getpass


HOST = ''  
PORT = 8080 
dir_base = '/scratch/convidado/Downloads/TPRedes-ServidorHTTP-main/Redes-TP'  

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(30)
print(f"Servidor escutando na porta: {PORT}")

clients = []
usernames = []


def send_response(client, response):
    client.sendall(response.encode('utf-8'))


def send_file(client, filename):
    file_path = os.path.join(dir_base, filename)
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        client.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {file_size}\r\nContent-Disposition: attachment; filename={filename}\r\n\r\n".encode('utf-8'))
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client.sendall(data)
    else:
        client.sendall(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nArquivo {filename} não encontrado.\n".encode('utf-8'))



def send_header(client, request):
    html = f"""
<html>
<head>
<title>Diretorio Base</title>
</head>
<body>
<h1>Diretorio base:</h1>
<p>{dir_base}</p>
</body>
</html>
"""
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}HTTP Request Header:\n\n{request}\n"
    client.sendall(response.encode('utf-8'))


def send_info(client):
    so = platform.platform()
    data = datetime.datetime.now().strftime('%Y-%m-%d ---- %H:%M')
    usuario = getpass.getuser()

    html = f"""
<html>
<head>
<title>Informacoes do computador</title>
</head>
<body>
<h1>Informacoes do computador:</h1>
<p>Sistema operacional: {so}</p>
<p>Data: {data}</p>
<p>Nome do usuario: {usuario}</p>
</body>
</html>
"""
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
    client.sendall(response.encode('utf-8'))


def handle(client, address):
    #while True:
        try:
            request = client.recv(1024).decode('utf-8')
            request_lines = request.split('\r\n')
            first_line = request_lines[0]
            method, path, http_version = first_line.split(' ')
            if method == 'GET':
                if path == '/':
                    file_list = os.listdir(dir_base)
                    #file_list_show = '\n'.join(file_list)
                    html = f"""
<html>
<head>
<title>Lista de arquivos no servidor</title>
</head>
<body>
<h1>Lista de arquivos no servidor:</h1>
<ul>
"""
                    for filename in file_list:
                        file_url = f"/download/{filename}"
                        html += f"<li><a href='{file_url}'>{filename}</a></li>\n"
                    html += """
</ul>
<h1>Para obter o Header digite '/HEADER' no cabecalho do navegador</h1>
<h1>Repositorio do GitHub: https://github.com/ferraz07/TPRedes-ServidorHTTP</h1>
</body>
</html>
"""
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
                    send_response(client, response)
                elif path.startswith('/download/'):
                    filename = path.split('/')[2]
                    send_file(client, filename)
                elif path == '/HEADER':
                    send_header(client, request)
                elif path == '/INFO':
                    send_info(client)
                else:
                    client.sendall("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found\n".encode('utf-8'))
                    client.close()
                    #break
            else:
                client.sendall("HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n400 Bad Request\n".encode('utf-8'))
                client.close()
                #break
        except:
            client.close()
            #break


def serve():
    while True:
        client, address = tcp.accept()
        thread = threading.Thread(target=handle, args=(client, address))
        thread.start()


serve()
