# Uncomment this to pass the first stage
import sys
import os
import socket
from typing import Union
from threading import Thread

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
                 header: str = '',
                 body: str =''
                 ):
        self._version = version
        self._status = status

        if len(header) > 0:
            self._header = header
        else:
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
        self._body = body
        self.message = self._header + http_message._crlf + self._body

directory = ''

allowed_methods = ['GET', 'POST']

def handle_client(client_socket: socket):
    request_bytes = client_socket.recv(4096)
    request = request_bytes.decode('utf-8')

    # Parser HTTP request
    t = tokenizer(request, '\r\n')

    # Get the request line
    reqline = t.get_token(0)

    # Get headers
    headers = []
    for i in range(t.count())[1:]:
        token = t.get_token(i)
        if token == '':
            break
        headers.append(token)

    # Get request body
    body = t.get_token(i + 1)

    # Get request method and path
    t.reset()
    t.tokenize(reqline, ' ')
    method = t.get_token(0)
    path = t.get_token(1)

    print(f'Requested path: {path}')

    # Build HTTP response
    response = None

    try:
        if method not in allowed_methods:
            response = http_message(405)

        elif path == '/':
            response = http_message()

        elif path.find('echo') == 1:
            t.reset()
            t.tokenize(path, '/')
            arg = path[path.find(t.get_token(2)):]

            response = http_message()
            response.add_header('Content-Type', 'text/plain')
            response.add_header('Content-Length', str(len(arg)))
            response.add_body(arg)

        elif path == '/user-agent':
            useragent = ''
            useragent_hdr = ''

            for h in headers:
                if h.find('User-Agent') != -1:
                    useragent_hdr = h
                    break

            if useragent_hdr != '':
                t.reset()
                t.tokenize(useragent_hdr, ' ')
                useragent = t.get_token(1)

            if useragent != '':
                response = http_message()
                response.add_header("Content-Type", "text/plain");
                response.add_header("Content-Length", str(len(useragent)));
                response.add_body(useragent);

        elif path.find('files') == 1:
            global directory
            if len(directory) == 0:
                response = http_message(404)

            else:
                t.reset()
                t.tokenize(path, '/');
                filename = path[path.find(t.get_token(2)):]
                filepath = directory + '/' + filename

                if method == 'GET':
                    if not os.path.exists(filepath):
                        response = http_message(404)

                    else:
                        stinfo = os.stat(filepath)

                        data = ''
                        with open(filepath, 'r') as f:
                            data = f.read()
                        if len(data) != stinfo.st_size:
                            response = http_message(500)

                        else:
                            response = http_message()
                            response.add_header(
                                "Content-Type", "application/octet-stream"
                            )
                            response.add_header(
                                "Content-Disposition",
                                { "attachment", f'filename="{filename}"' }
                            )
                            response.add_header("Content-Length", str(stinfo.st_size))
                            response.add_body(data)
                elif method == 'POST':
                    nwrite = 0
                    with open(filepath, 'w') as f:
                        nwrite = f.write(body)
                    if len(body) != nwrite:
                        response = http_message(500)

                    else:
                        response = http_message(201)

    except Exception as e:
        sys.stderr.write(f'Exception occurred: {e}\n')

    finally:
        if response is None:
            response = http_message(404)

    response_bytes = response.message.encode()
    client_socket.send(response_bytes)

    client_socket.close()

def main():
    if len(sys.argv) == 3:
        if sys.argv[1] == '--directory':
            global directory
            directory = sys.argv[2]

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    server_socket = socket.create_server(("localhost", 4221),
                                         backlog=5,
                                         reuse_port=True)

    MAX_CONCURRENT_CONN = 5
    client_threads = []
    num_conn = 0

    while num_conn < MAX_CONCURRENT_CONN:
        client_socket, address = server_socket.accept() # wait for client
        t = Thread(target=handle_client, args=(client_socket,))
        client_threads.append(t)
        t.start()
        num_conn += 1

    for t in client_threads: t.join()

if __name__ == "__main__":
    main()
