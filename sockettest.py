import socket
from datetime import datetime

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 12345))
server_socket.listen(0)

client_socket, addr = server_socket.accept()
data = client_socket.recv(65535)

request_data = data.decode().split()
request_method = request_data[0]
request_version = request_data[2]

server_name = "Python Light-Weight Server"

if request_method == "GET":
    response_data = "{0} 200 OK\nServer: {1}\nDate: {2}\n".format(request_version, server_name,
    datetime.now().strftime('%a, %d %b %Y %H:%M:%S KST'))
else:
    response_data = "{0} 405 Method Not Allowed\nServer: {1}\nDate: {2}\n".format(request_version, server_name,
    datetime.now().strftime('%a, %d %b %Y %H:%M:%S KST'))


client_socket.send(response_data.encode())

