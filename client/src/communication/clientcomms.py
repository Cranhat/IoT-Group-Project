import os
import socket
import ssl
from pathlib import Path


class SecureClient:
    def __init__(self, port=3000, buf_size=99):
        self.port = port
        self.buf_size = buf_size
        self.sfd = None

        self.ctx = self._create_ssl_context()

    # def _create_ssl_context(self):
    #     ctx = ssl.create_default_context()
    #     ctx.load_cert_chain("client0.crt", "client0.key")
    #     ctx.load_verify_locations("ca.pem")
    #     ctx.verify_mode = ssl.CERT_REQUIRED
    #     return ctx
    
    def _create_ssl_context(self):
        ctx = ssl.create_default_context()
        cert_dir = Path(__file__).resolve().parent

        cert_path = cert_dir / "client0.crt"
        key_path = cert_dir / "client0.key"
        ca_path = cert_dir / "ca.pem"

        missing = [str(p) for p in (cert_path, key_path, ca_path) if not p.exists()]
        if missing:
            raise FileNotFoundError(f"Missing TLS file(s): {', '.join(missing)}")

        ctx.load_cert_chain(
            str(cert_path),
            str(key_path),
        )
        ctx.load_verify_locations(str(ca_path))
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx

    def start(self):
        host = input("input server ip: ")

        try:
            self.connect(host)
            
            while True:
                self.send_loop()
                self.recv_loop()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self._cleanup()

    def connect(self, host):
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
                    server_hostname=os.environ.get("TLS_SERVER_HOSTNAME", "serv")
                )

                return  # sukces

            except Exception as e:
                print(f"client: connect error: {e}")
                if self.sfd:
                    self.sfd.close()
                    self.sfd = None

        raise ConnectionError("client: failed to connect")

    def send_loop(self):
        try:
            msg = input()
            if not msg:
                return False

            self.sfd.sendall((msg + "\n").encode())
            
            return True

        except Exception as e:
            print(f"send error: {e}")
            return False
        
    def send_loop(self, message: str):
        try:
            msg = message
            if not msg:
                return False

            self.sfd.sendall((msg + "\n").encode())
            
            return True

        except Exception as e:
            print(f"send error: {e}")
            return False

    def recv_loop(self) -> str | None:
        try:
            data = self.sfd.recv(self.buf_size - 1)

            if not data:
                print("client recv: connection closed")
                return None
            
            return data.decode()

        except Exception as e:
            print(f"recv error: {e}")
            return None    
              

    def _cleanup(self):
        if self.sfd:
            self.sfd.close()


if __name__ == "__main__":
    client = SecureClient()
    client.start()
