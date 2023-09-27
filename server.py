#  coding: utf-8
import socketserver
import os

# Copyright 2023 Julian Gallego Franco, Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved

BUFFER_SIZE = 4096

HOST = "localhost"
PORT = 8080


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        reqHeaders = self.request.recv(BUFFER_SIZE).decode(
            'utf-8').strip().split('\n')
        reqComponents = reqHeaders[0].strip().split()

        hostCount = 0
        for header in reqHeaders:
            if header.startswith("Host:"):
                hostCount += 1

        if hostCount != 1:
            # Sent to any HTTP/1.1 requests that lack or contain more than one Host header field
            self.sendErrorResponse("400 Bad Request")
            return

        if len(reqComponents) < 2:
            # Sent to any HTTP/1.1 requests that lack a Method and Path
            self.sendErrorResponse("400 Bad Request")
            return

        method = reqComponents[0]
        if method != "GET":
            # Sent to any HTTP/1.1 requests whose method is not GET
            self.sendErrorResponse("405 Method Not Allowed")
            return

        path = reqComponents[1]
        filePath = os.path.abspath(os.path.join('./www', path.strip('/')))

        if not os.path.exists(filePath) or not filePath.startswith(os.path.abspath('./www')):
            # Path does not exits or points in incorrect directory
            self.sendErrorResponse("404 Not Found")
            return

        if not path.endswith('/') and not os.path.isfile(filePath):
            # Valid direcoty path missing a trailing /
            self.sendRedirectResponse(
                "301 Moved Permanently", os.path.normpath(path) + '/')
            return

        if path.endswith('/'):
            # Return index.html for any valid paths ending in /
            filePath = os.path.join(filePath, 'index.html')

        try:
            with open(filePath, 'rb') as file:
                content = file.read()
                contentType = self.getContentType(filePath)
                self.sendSuccessResponse(content, contentType)
        except Exception:
            self.sendErrorResponse("500 Internal Server Error")

    def getContentType(self, filePath):
        # Get the correct response content type
        extension = os.path.splitext(filePath)[1]

        if extension == ".html":
            return "text/html"
        elif extension == ".css":
            return "text/css"

        return "text/plain"

    def sendSuccessResponse(self, content, type):
        # Serve file
        res = f'HTTP/1.1 200 OK\r\n'
        res += f'Content-Type: {type}; charset=utf-8\r\n'
        res += f'Content-Length: {len(content)}\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'
        res = res.encode('utf-8') + content

        self.request.sendall(res)

    def sendRedirectResponse(self, status, location):
        # Redirect to correct path
        res = f'HTTP/1.1 {status}\r\n'
        res += 'Content-Type: text/html; charset=utf-8\r\n'
        res += f'Location: {location}\r\n'
        res += f'Content-Length: 0\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'

        self.request.sendall(res.encode('utf-8'))

    def sendErrorResponse(self, status):
        # Send error response
        res = f'HTTP/1.1 {status}\r\n'
        res += 'Content-Type: text/html; charset=utf-8\r\n'
        res += f'Content-Length: 0\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'

        self.request.sendall(res.encode('utf-8'))


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    server.serve_forever()
