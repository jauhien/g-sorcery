#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    server.py
    ~~~~~~~~~
    
    test server
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import threading

from g_sorcery.compatibility import py2k

if py2k:
    from SocketServer import TCPServer as HTTPServer 
    from SimpleHTTPServer import SimpleHTTPRequestHandler
else:
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler

class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        HTTPServer.allow_reuse_address = True
        server_address = ('127.0.0.1', 8080)
        self.httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        self.httpd.shutdown()
