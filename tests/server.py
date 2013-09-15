#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    server.py
    ~~~~~~~~~
    
    test server
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import os
import threading

from g_sorcery.compatibility import py2k

if py2k:
    from SocketServer import TCPServer as HTTPServer 
    from SimpleHTTPServer import SimpleHTTPRequestHandler
else:
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler

def HTTPRequestHandlerGenerator(direct):

    class HTTPRequestHandler(SimpleHTTPRequestHandler):
        directory = direct

        def __init__(self, request, client_address, server):
            super(HTTPRequestHandler, self).__init__(request, client_address, server)

        def translate_path(self, path):
            return os.path.join(self.directory, path[1:])

    return HTTPRequestHandler

    
class Server(threading.Thread):
    def __init__(self, directory):
        super(Server, self).__init__()
        HTTPServer.allow_reuse_address = True
        server_address = ('127.0.0.1', 8080)
        self.httpd = HTTPServer(server_address, HTTPRequestHandlerGenerator(directory))
    
    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        self.httpd.shutdown()
