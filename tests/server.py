#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    server.py
    ~~~~~~~~~
    
    test server
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import http.server, threading

class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        server_address = ('127.0.0.1', 8080)
        self.httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    
    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        self.httpd.shutdown()
