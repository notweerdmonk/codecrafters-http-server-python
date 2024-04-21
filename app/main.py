# Uncomment this to pass the first stage
import socket
from typing import Union

class tokenizer(object):
    def _tokenize(self, data: str, delim: str):
        self._tokens = data.split(delim)

    def __init__(self, data: str, delim: str):
        self._tokenize(data, delim)

    def tokenize(self, data: str, delim: str):
        self._tokenize(data, delim)

    def count(self):
        return len(self._tokens)

    def get_tokens(self):
        return self._tokens

    def get_token(self, i):
        return self._tokens[i] if i < self.count() else ''

    def reset(self):
        self._tokens.clear()

class http_message(object):
    _crlf = '\r\n'
    _http_response_status = {
        200: ( '200', 'OK' ),
        201: ( '201', 'Created' ),
        302: ( '302', 'Found' ),
        400: ( '400', 'Bad Request' ),
        401: ( '401', 'Unauthorized' ),
        403: ( '403', 'Forbidden' ),
        404: ( '404', 'Not Found' ),
        405: ( '405', 'Method Not Allowed' ),
        500: ( '500', 'Internal Server Error' )
    }

    def __init__(self,
                 status: int =200,
                 version: str ='1.1',
                 body: str =''
                 ):
        self._version = version
        self._status = status

        code, status = http_message._http_response_status[self._status]
        self._header = f'HTTP/{self._version} {code} {status}{http_message._crlf}'

        self._body = body

        self.message = self._header + http_message._crlf + self._body

    def add_header(self, key: str, value: Union[str, list]):
        if len(key) == 0:
            return

        if isinstance(value, list):
            self._header += key + ': '
            for v in value:
                self._header += v + ';'
            self._header += http_message._crlf
        else:
            self._header += f'{key}: {value}{http_message._crlf}'

        self.message = self._header + http_message._crlf + self._body

    def add_body(self, body: str):
        self.message = self._header + http_message._crlf + self._body

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, address = server_socket.accept() # wait for client

    request_bytes = client_socket.recv(4096)
    request = request_bytes.decode('utf-8')

    # Parser HTTP request
    t = tokenizer(request, '\r\n')
    # Get the request line
    reqline = t.get_token(0)
    # Get request method and path
    t.reset()
    t.tokenize(reqline, ' ')
    method = t.get_token(0)
    path = t.get_token(1)

    # Build HTTP response
    response = None
    if method != 'GET':
        response = http_message(405)
    elif path == '/':
        response = http_message()
    else:
        response = http_message(404)

    response_bytes = response.message.encode()
    client_socket.send(response_bytes)

    client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    main()
