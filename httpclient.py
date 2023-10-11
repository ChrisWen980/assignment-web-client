#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Chris Wen
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        if data:
            return int(data.split()[1])
        return None

    def get_headers(self,data):
        if data:
            return data.split('\r\n')[:-1]
        return None

    def get_body(self, data):
        if data:
            return data.split('\r\n')[-1]
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

######################################################################################################################################################
# Function Purpose: Parses the url provided for the host, port, and path
# Returns: - Host: The url hostname
#          - Port: The url port
#          - Path: The url path
######################################################################################################################################################
    def parseUrl(self, url):
        parsedUrl = urllib.parse.urlparse(url)

        if parsedUrl.hostname:
            host = parsedUrl.hostname

        if parsedUrl.port:
            port = parsedUrl.port
        elif parsedUrl.scheme == 'http':
            port = 80
        elif parsedUrl.scheme == 'https':
            port = 443

        if parsedUrl.path:
            path = f'{parsedUrl.path}'
            if parsedUrl.query:
                path += f'?{parsedUrl.query}'
            if parsedUrl.fragment:
                path += f'#{parsedUrl.fragment}'
        else:
            path = '/'

        return host, port, path

######################################################################################################################################################
# Function Purpose: Sends the request then receives the data, and parses the data for the HTTP code and the HTTP body.
# Returns: - Code: The HTTP code
#          - Body: The HTTP body
######################################################################################################################################################
    def getContent(self, host, port, request):
        self.connect(host, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        return code, body

    def GET(self, url, args=None):
        host, port, path = self.parseUrl(url)
        request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n'
        code, body = self.getContent(host, port, request)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.parseUrl(url)
        request = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\n'
        if args:
            parsedArgs = urllib.parse.urlencode(args)
            request += 'Content-Type: application/x-www-urlencoded\r\n'
            request += f'Content-Length: {len(parsedArgs.encode("utf-8"))}\r\n'
        else:
            request += 'Content-Length: 0\r\n'
        request += f'Connection: close\r\n\r\n'
        if args:
            request += parsedArgs
        code, body = self.getContent(host, port, request)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
