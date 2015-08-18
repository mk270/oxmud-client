import struct
import os
import pwd
import sys
import magic_numbers

def calc_payload(pkt, ip_address, hostname):
    data = map(ord, pkt) # self.input_buffer)
    if len(data) < 7:
        return
    seed, = struct.unpack('<I', pkt[3:7])
    prefix = "\xff\xff\x02"

    username = pwd.getpwuid(os.getuid()).pw_name
    tty = os.ttyname(sys.stdin.fileno())

    if hostname is None:
        hostname = username
    identities = [username, ip_address, tty, hostname]
    message = struct.pack("10s20s20s37s", *identities).replace('\0', " ")
    message += "   " # self.input_buffer[0:3]
    assert len(message) == 90

    shiftreg = magic_numbers.RND_NUM1
    for i in xrange(0, 90):
        shiftreg = ((shiftreg * magic_numbers.RND_NUM2 +
                     (ord(message[i]) & 0xFF)) & 0xFFFFFF)

    for i in xrange(0, magic_numbers.RND_NUM3):
        feedback = shiftreg & seed
        feedback = (feedback ^ (feedback >> 16)) & 0xFFFF
        feedback = (feedback ^ (feedback >> 8)) & 0xFF
        feedback = (feedback ^ (feedback >> 4)) & 0xF
        feedback = (feedback ^ (feedback >> 2)) & 0x3
        feedback = (feedback ^ (feedback >> 1)) & 0x1
        shiftreg = ((shiftreg & 0x7FFFFFFF)<<1) ^ feedback ^ ((shiftreg >> 31) & 0x1)

    token = struct.pack('<I', shiftreg)
    token = "".join(map(lambda c: chr(ord(c) | 0x80), token))
    payload = prefix + message + token + '\0'
    assert len(payload) == 98
    return payload
