"""
IoT Client - connects to server, executes tasks, reports status.
Can run on local PC (Linux / WSL) as well as remote Raspberry Pi.
Usage: python3 client.py
"""

import socket
import ssl
import threading
import time

from config import CA_CERT, CLIENT_CERT, CLIENT_KEY, PORT, SERVER_HOST, TLS_SERVER_HOSTNAME, USE_TLS
from task_exec import heartbeat_loop, receive_loop, task_worker


def make_client_socket() -> socket.socket:
    """
    Create client's socket for communication. Use TLS if available.

    Returns:
        socket.socket: Client's communication socket.
    """
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if USE_TLS:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(CA_CERT)
        ctx.load_cert_chain(CLIENT_CERT, CLIENT_KEY)
        ctx.check_hostname = True
        return ctx.wrap_socket(raw, server_hostname=TLS_SERVER_HOSTNAME)

    return raw


def main():
    retry_delay = 2

    while True:
        try:
            sock = make_client_socket()
            sock.connect((SERVER_HOST, PORT))
            retry_delay = 2

            threads = [
                threading.Thread(target=heartbeat_loop, args=(sock,), daemon=True),
                threading.Thread(target=task_worker, args=(sock,), daemon=True),
                threading.Thread(target=receive_loop, args=(sock,), daemon=True),
            ]

            for t in threads:
                t.start()

            threads[2].join()
            sock.close()

        except (ConnectionRefusedError, OSError) as e:
            print(f"[CLIENT] Could not connect: {e}")

        print(f"[CLIENT] Reconnecting in {retry_delay}s...")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CLIENT] Exiting.")
