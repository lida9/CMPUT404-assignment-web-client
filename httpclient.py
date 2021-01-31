#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __str__(self):
        return str(self.code) + "\n\n" + self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data = data.splitlines()
        code = data[0].split()[1] # get the code
        return int(code)

    def get_headers(self,data):
        index = data.find("\r\n")
        end_index = data.find("\r\n\r\n")
        headers = data[index+2:end_index]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def parse_url(self, url):
        parsed = urllib.parse.urlparse(url)
        # returns base host and path
        path = parsed.path if parsed.path != "" else "/"
        port = parsed.port if parsed.port != None else 80
        return parsed.hostname, port, path

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

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)

        self.connect(host, int(port))
        # compose request
        request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        # get response code and body
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)
        self.connect(host, int(port))

        # compose request
        request = (
            f'POST {path} HTTP/1.1\r\n'
            f'Host: {host}\r\n'
            f'Connection: close\r\n'
            f'Content-Type: application/x-www-form-urlencoded\r\n'
            f'Content-Length: ')
        if args == None:
            length = 0
            params = ""
        else:
            # url encode arguments and get length
            params = urllib.parse.urlencode(args)
            length = len(params)

        request += str(length) + '\r\n\r\n' + params

        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        # get response code and body
        code = self.get_code(data)
        body = self.get_body(data)
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
