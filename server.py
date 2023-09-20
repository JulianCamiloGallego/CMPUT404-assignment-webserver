#  coding: utf-8
import socketserver
import os

# Copyright 2023 Julian Gallego Franco
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

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        headers = self.data.decode('utf-8').split('\n')
        request = headers[0].strip().split()
        
        if len(request) < 2:
            self.sendErrorResponse("400 Bad Request")
            return

        method = request[0]
        if method != "GET":
            self.sendErrorResponse("405 Method Not Allowed")
            return
        
        path = request[1]
        filePath = os.path.abspath(os.path.join('./www', path.strip('/')))
        
        if not os.path.exists(filePath) or not filePath.startswith(os.path.abspath('./www')):
            self.sendErrorResponse("404 Not Found")
            return

        if not path.endswith('/') and not os.path.isfile(filePath):
            self.sendRedirectResponse("301 Moved Permanently", path + '/')
            return
        
        if path.endswith('/'):
            filePath = os.path.join(filePath, 'index.html')
        
        try:
            with open(filePath, 'rb') as file:
                content = file.read()
                contentType = self.getContentType(filePath)
                self.sendSuccessResponse(content, contentType)

        except FileNotFoundError:
            self.sendErrorResponse("404 Not Found")

    def getContentType(self, filePath):
        ext = os.path.splitext(filePath)[1]
        
        if ext == ".html":
            return "text/html"
        elif ext == ".css":
            return "text/css"
        
        return "text"

    def sendSuccessResponse(self, content, type):
        # headers
        res = f'HTTP/1.0 200 OK\r\n'
        res += 'Cache-Control: no-cache\r\n'
        res += f'Content-Type: {type}; charset=utf-8\r\n'
        res += f'Content-Length: {len(content)}\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'
        # body
        res = res.encode('utf-8') + content

        self.request.sendall(res)

    
    def sendRedirectResponse(self, status, location):
        # headers
        res = f'HTTP/1.0 {status}\r\n'
        res += 'Content-Type: text/html; charset=utf-8\r\n'
        res += f'Location: {location}\r\n'
        res += 'Content-Length: 0\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'

        self.request.sendall(res.encode('utf-8'))

    def sendErrorResponse(self, status):
        # headers
        res = f'HTTP/1.0 {status}\r\n'
        res += 'Content-Type: text/html; charset=utf-8\r\n'
        res += 'Content-Length: 0\r\n'
        res += 'Connection: close\r\n'
        res += '\r\n'

        self.request.sendall(res.encode('utf-8'))



if __name__ == "__main__":
    HOST = "localhost" 
    PORT = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    server.serve_forever()
