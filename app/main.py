# Uncomment this to pass the first stage
import socket
from typing import Union

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
                 version: str ='1.1',
                 status: int =200,
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

    client_socket.recv(4096)

    response = http_message().message.encode()
    client_socket.send(response)

    client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    main()
