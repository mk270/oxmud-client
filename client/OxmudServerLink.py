
import os
import sys
import socket
import time

from Networking import zap_cr
from ServerLink import ServerLink

this_hostname = os.uname()[1]
fallback_address = (this_hostname, 2093)

class OxmudServerLink(ServerLink):
    WPRK_MESSAGE = 1
    WPRK_PROMPT = 3
    WPRK_SECRET = 4
    WPRK_LOGOUT = 5
    WPRK_ACCEPT = 6

    def handshake(self, pkt):
        import handshake
        payload = handshake.calc_payload(pkt, self.ip_address, self.hostname)
        self.emit_raw(payload)
        self.handshaken = True

    def handleLine(self, pkt):
        ty = ord(pkt[2])
        data = pkt[3:]

        if ty == self.WPRK_MESSAGE:
            self.line_buffer += data

            if self.line_buffer[-1] == '\n':
                self.ss.emit_line(self.line_buffer.strip('\n'))
                self.line_buffer = ""
            else:
                pass
        elif ty == self.WPRK_PROMPT:
            self.ss.set_prompt(data, refresh=True)
        elif ty == self.WPRK_SECRET:
            self.ss.set_password_mode(True)
        elif ty == self.WPRK_ACCEPT:
            if not self.handshaken:
                self.handshake(pkt)
            else:
                self.ss.emit_line("double handshake")
        elif ty == self.WPRK_LOGOUT:
            pass
        else:
            self.ss.emit_line("WARNING: unhandled packet type: %d" % ty)

    def get_delim(self):
        return "\0"

    def emit(self, data):
        prefix = '\xff\xff\x02'
        payload = prefix + data + '\0'
        self.emit_raw(payload)

    def send_oxmud_init_msg(self):
        self.emit_raw('%c%c%c%c' % (0xff, 0xff, 6, 0))

    def setup(self):
        try:
            self.send_oxmud_init_msg()
        except socket.error:
            self.attempt_rescue()
            self.send_oxmud_init_msg()
        self.handshaken = False
        self.line_buffer = "" # for unterminated strings sent by server

    def attempt_rescue(self):
        # tell the user what's going on
        self.ss.emit_line("Connection problem - trying workaround")
        self.ss.emit_line(self.connection_failed)
        throwaway = socket.socket()
        hostname, port = fallback_address
        throwaway.connect((hostname, port))
        throwaway.close()
        time.sleep(0.5)
        self.s.setblocking(1)
        self.basic_setup()
