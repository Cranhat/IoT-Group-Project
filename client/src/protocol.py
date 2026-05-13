"""
Simple message protocol over a TCP/TLS stream.
Each message is a JSON object terminated by a newline character.
"""

import json


def send_msg(sock, msg: dict):
    """Serialize dict to JSON and send over socket."""
    data = json.dumps(msg) + "\n"
    sock.sendall(data.encode("utf-8"))


def recv_msg(sock) -> dict:
    """Read one newline-terminated JSON message from socket."""
    buf = b""
    while True:
        chunk = sock.recv(4096)

        buf += chunk
        if b"\n" in buf:
            line, _ = buf.split(b"\n", 1)
            return json.loads(line.decode("utf-8"))