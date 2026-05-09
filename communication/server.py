import socket
import ssl


class SecureServer:
    def __init__(self, host="0.0.0.0", port=3000, backlog=5, buf_size=1024):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.buf_size = buf_size

        self.sfd = None
        self.cfd = None
        self.addr = None

        self.ctx = self._create_ssl_context()

    def _create_ssl_context(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3

        ctx.load_cert_chain("server.crt", "server.key")
        ctx.load_verify_locations("ca.pem")
        ctx.verify_mode = ssl.CERT_NONE

        return ctx

    def start(self):
        try:
            self._create_socket()
            self._accept_connection()
            self._handle_client()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self._cleanup()

    def _create_socket(self):
        self.sfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Server socket = {self.sfd.fileno()}")

        self.sfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sfd.bind((self.host, self.port))
        self.sfd.listen(self.backlog)

        print("server: waiting to connect...")

    def _accept_connection(self):
        raw_cfd, self.addr = self.sfd.accept()
        self.cfd = self.ctx.wrap_socket(raw_cfd, server_side=True)

        print(f"Accepted socket fd = {self.cfd.fileno()}")
        print(f"Connection from {self.addr}")

    def _handle_client(self):
        while True:
            data = self.cfd.recv(self.buf_size - 1)

            if not data:
                print("server recv: connection closed")
                break

            msg = data.decode()
            print(f"message [{len(data)}]:\n{msg}")

            response = f"echo: {msg}"
            self.cfd.sendall(response.encode())

    def _cleanup(self):
        try:
            if self.cfd:
                self.cfd.close()
        except:
            pass

        if self.sfd:
            self.sfd.close()


if __name__ == "__main__":
    server = SecureServer()
    server.start()
