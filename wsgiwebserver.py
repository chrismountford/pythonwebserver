"""
First, the server starts and loads an ‘application’ callable provided by your Web framework/application
Then, the server reads a request
Then, the server parses it
Then, it builds an ‘environ’ dictionary using the request data
Then, it calls the ‘application’ callable with the ‘environ’ dictionary and a ‘start_response’ callable as parameters and gets back a response body.
Then, the server constructs an HTTP response using the data returned by the call to the ‘application’ object and the status and response headers set by the ‘start_response’ callable.
And finally, the server transmits the HTTP response back to the client
"""

import io
import socket
import sys

class WSGIServer(object):
    addressFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    requestQueueSize = 1

    def __init__(self, serverAddress):
        # Create a listening socket
        self.listenSocket = listenSocket = socket.socket(
            self.addressFamily,
            self.socketType
        )

        # Allow to reuse the same address
        listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind
        listenSocket.bind(serverAddress)

        # Activate
        listenSocket.listen(self.requestQueueSize)

        # Get server host name and port
        host, port = self.listenSocket.getsockname()[:2]

        self.serverName = socket.getfqdn(host)
        self.serverPort = port

        # Return headers set by web framework/web application
        self.headersSet = []

    def setApp(self, application):
        self.application = application

    def serveForever(self):
        listenSocket = self.listenSocket
        while True:
            # New client connection
            self.clientConnection, clientAddress = listenSocket.accept()

            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handleOneRequest()

    def handleOneRequest(self):
        requestData = self.clientConnection.recv(1024)
        self.requestData = requestData = requestData.decode('utf-8')

        # Print formatted request data a la 'curl -v'
        print(''.join(f'< {line}\n' for line in requestData.splitlines()))

        self.parseRequest(requestData)

        # Construct environment dictionary using request data
        env = self.getEnviron()

        # Its time to call our application callable and get
        # back a result taht will become HTTP response body
        result = self.application(env, self.startReponse)

        # Construct a response and send it back to the client
        self.finishResponse(result)

    def parseRequest(self, text):
        requestLine = text.splitlines()[0]
        requestLine = requestLine.rstrip('\r\n')

        # Break down the request line into components
        (self.requestMethod,  # GET
        self.path,  #/hello
        self.requestVersion  # HTTP/1.1
        ) = requestLine.split()

    def getEnviron(self):
        env = {}

        # Required WSGI variables
        env['wsgi_version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.requestData)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi_run_once'] = False

        # Required CGI variables
        env['REQUEST_METHOD'] = self.requestMethod
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.serverName
        env['SERVER_PORT'] = str(self.serverPort)

        return env

    def startReponse(self, status, responseHeaders, excInfo=None):
        # Add necessary server headers
        serverHeaders = [
            ('Date', 'Fri, 20 Aug 2021 10:30:00 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]

        self.headersSet = [status, responseHeaders + serverHeaders]
        # To adhere to WSGI specification the startResponse must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finishResponse

    def finishResponse(self, result):
        try:
            status, responseHeaders = self.headersSet
            response = f'HTTP/1.1 {status}\r\n'
            for header in responseHeaders:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n';

            for data in result:
                response += data.decode('utf-8')
            
            # Print formatted response data a la 'curl -v'
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))
            responseBytes = response.encode()
            self.clientConnection.sendall(responseBytes)
        finally:
            self.clientConnection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def makeServer(serverAddress, application):
    server = WSGIServer(serverAddress)
    server.setApp(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    appPath = sys.argv[1]
    module, application = appPath.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = makeServer(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serveForever()
