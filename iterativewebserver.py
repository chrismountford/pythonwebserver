import socket

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5

def handleRequest(clientConnection):
    request = clientConnection.recv(1024)
    print(request.decode())
    httpResponse = b"""
HTTP/1.1 200 OK

Hello world!
    """

    clientConnection.sendall(httpResponse)

def serveForever():
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.setsockopt(socket.SOL_SOCKET, socker.SO_REUSEADDR, 1)
    listenSocket.bind(SERVER_ADDRESS)
    listenSocket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    while True:
        clientConnection, clientAddress = listenSocket.accept()
        handleRequest(clientConnection)
        clientConnection.close()

if __name__ == '__main__':
    serveForever()
