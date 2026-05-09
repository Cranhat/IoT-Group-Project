import socket
import ssl


class SecureClient:
    def __init__(self, port=3000, buf_size=99):
        self.port = port
        self.buf_size = buf_size
        self.sfd = None

        self.ctx = self._create_ssl_context()

    def _create_ssl_context(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def start(self):
        host = input("input server ip: ")

        try:
            self._connect(host)
            self._chat_loop()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self._cleanup()

    def _connect(self, host):
        addr_info = socket.getaddrinfo(
            host,
            self.port,
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        for family, socktype, proto, canonname, sockaddr in addr_info:
            try:
                self.sfd = socket.socket(family, socktype, proto)
                print(f"Server socket = {self.sfd.fileno()}")

                self.sfd.connect(sockaddr)
                self.sfd = self.ctx.wrap_socket(
                    self.sfd,
                    server_hostname=host
                )

                return  # sukces

            except Exception as e:
                print(f"client: connect error: {e}")
                if self.sfd:
                    self.sfd.close()
                    self.sfd = None

        raise ConnectionError("client: failed to connect")

    def _chat_loop(self):
        while True:
            mesg = input()
            mesg += "\n"

            self.sfd.sendall(mesg.encode())

            data = self.sfd.recv(self.buf_size - 1)

            if not data:
                print("client recv: connection closed")
                break

            print(data.decode())

    def _cleanup(self):
        if self.sfd:
            self.sfd.close()


if __name__ == "__main__":
    client = SecureClient()
    client.start()
