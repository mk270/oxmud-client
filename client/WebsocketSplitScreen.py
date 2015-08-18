
# Archipelago, a multi-user dungeon (MUD) server, by Martin Keegan
#
# Copyright (C) 2009-2012  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the GNU Affero General Public Licence as published by
# the Free Software Foundation, either version 3 of said Licence, or
# (at your option) any later version.

from OxmudSplitScreen import OxmudSplitScreen

import sys
import os

import struct
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO



class Throbber(object):
    def __init__(self):
        pass
    def next(self):
        pass


class WebsocketSplitScreen(OxmudSplitScreen):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def __init__(self):
        self.sock = None
        self.prompt = '> '
        self.new_cmd()
        self.password_mode = False
        self.server_link = None
        self.delay_until = None
        self.throbber = Throbber()
        self.handshake_done = False
        self.outbuf = []

    def fixup_line(self, line):
        return line.replace('\0', '0')

    def setup(self):
        pass

    def write_prompt(self):
        pass

    def emit_line(self, line):
        if not self.handshake_done:
            self.outbuf.append(line)
        else:
            if len(self.outbuf):
                for l in self.outbuf:
                    self.send_message(l)
                self.outbuf = []
            self.send_message(line)

    def on_message(self, data):
        self.sock.emit(data)

    def handle_input(self):
        if self.handshake_done:
            self.read_next_message()
        else:
            self.handshake()

    def place_cursor(self):
        pass

    def set_prompt(self, new_prompt, refresh=False):
        pass

    def send_message(self, message):

        with file('/tmp/done', 'w') as f:
            f.write("got here senf message\n")

        os.write(1, chr(129))
        length = len(message)
        if length <= 125:
            os.write(1, chr(length))
        elif length >= 126 and length <= 65535:
            os.write(1, 126)
            os.write(1, struct.pack(">H", length))
        else:
            os.write(1, 127)
            os.write(1, struct.pack(">Q", length))
        os.write(1, message)

    def read_next_message(self):

        import traceback

        with file('/tmp/done', 'w') as f:
            f.write("got here: read message\n")

            try:
                data = os.read(0, 2)
                f.write("len: %d\n" % len(data))
                length = ord(data[1]) & 127
                if length == 126:
                    length = struct.unpack(">H", os.read(0, 2))[0]
                elif length == 127:
                    length = struct.unpack(">Q", os.read(0, 8))[0]
                masks = [ord(byte) for byte in os.read(0, 4)]
                decoded = ""
                for char in os.read(0, length):
                    decoded += chr(ord(char) ^ masks[len(decoded) % 4])
                self.on_message(decoded)
            except:
                f.write(traceback.format_exc())
                raise



    def handshake(self):
        data = ""
        for attempt in xrange(0, 20):
            data += os.read(0, 1024)#.strip()
            data = data.replace("\n\n", "\r\n")
            with file('/tmp/log', 'w') as f:
                f.write(data)
            try:
                headers = Message(StringIO(data.split('\r\n', 1)[1]))
                if headers.get("Upgrade", None) == "websocket":
                    break
            except:
                continue
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        
        if headers.get("Upgrade", None) == "websocket":
            return
        
        key = headers['Sec-WebSocket-Key']

        digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
        response = 'HTTP/1.1 101 Switching Protocols\r\n'
        response += 'Upgrade: websocket\r\n'
        response += 'Connection: Upgrade\r\n'
        response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
        self.handshake_done = os.write(1, response)
