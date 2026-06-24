"""
Simple message protocol over a TCP/TLS stream.
Each message is a JSON object terminated by a newline character.
"""

import json
from communication.clientcomms import SecureClient


def send_msg(comms: SecureClient, msg: dict):
    """Serialize dict to JSON and send over socket."""
    data = json.dumps(msg) + "\n"
    comms.send_loop(data.encode("utf-8"))


def recv_msg(comms: SecureClient) -> dict:
    """Read one newline-terminated JSON message from socket."""
    buf = b""
    while True:
        chunk = comms.recv_loop()

        buf += chunk
        if b"\n" in buf:
            line, _ = buf.split(b"\n", 1)
            return json.loads(line.decode("utf-8"))