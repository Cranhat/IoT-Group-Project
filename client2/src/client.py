from task_exec import *
from communication.clientcomms import SecureClient
from config import PORT, SERVER_HOST, USE_TLS
import socket


class ClientConnection:
    """Adapter used by task/protocol code for either TLS or plain TCP."""

    def __init__(self, port: int, use_tls: bool):
        self.port = port
        self.use_tls = use_tls
        self._secure = SecureClient(port=port) if use_tls else None
        self.sfd = None

    def connect(self, host: str):
        if self.use_tls:
            self._secure.connect(host)
            self.sfd = self._secure.sfd
            return

        self.sfd = socket.create_connection((host, self.port))

    def send_loop(self, message):
        if self.sfd is None:
            raise OSError("client socket is not connected")

        if isinstance(message, str):
            payload = message.encode("utf-8")
        else:
            payload = message

        self.sfd.sendall(payload)
        return True

    def recv_loop(self) -> bytes:
        if self.sfd is None:
            raise OSError("client socket is not connected")
        return self.sfd.recv(4096)

    def _cleanup(self):
        if self.sfd:
            self.sfd.close()
            self.sfd = None


def main():
    retry_delay = 2

    while True:
        comms = None
        try:
            comms = ClientConnection(port=PORT, use_tls=USE_TLS)
            comms.connect(SERVER_HOST)    # CHANGE TO SOCKET RECEIVED FROM COMMUNICATION SECTION !!!!!!!!!
            retry_delay = 2

            threads = [
                threading.Thread(target=heartbeat_loop, args=(comms,), daemon=True),
                threading.Thread(target=task_worker,    args=(comms,), daemon=True),
                threading.Thread(target=receive_loop,   args=(comms,), daemon=True),
            ]

            for t in threads:
                t.start()

            threads[2].join()
            # Close connection here if necessary

        except (ConnectionRefusedError, OSError) as e:
            print(f"[CLIENT] Could not connect: {e}")
        finally:
            if comms is not None:
                comms._cleanup()

        print(f"[CLIENT] Reconnecting in {retry_delay}s...")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CLIENT] Exiting.")
