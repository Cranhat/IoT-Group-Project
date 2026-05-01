import socket
import ssl

HOST = "0.0.0.0"
PORT = 3000
BACKLOG = 5
BUF_SIZE = 1024

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_3
ctx.maximum_version = ssl.TLSVersion.TLSv1_3

ctx.load_cert_chain("server.crt", "server.key")

ctx.load_verify_locations("ca.pem")
ctx.verify_mode = ssl.CERT_NONE

def server():
    try:
        sfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Server socket = {sfd.fileno()}")

        sfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sfd.bind((HOST, PORT))

        sfd.listen(BACKLOG)
        print("server: waiting to connect...")

        cfd, addr = sfd.accept()
        cfd = ctx.wrap_socket(cfd, server_side=True)
        print(f"Accepted socket fd = {cfd.fileno()}")
        print(f"Connection from {addr}")

        while True:
            data = cfd.recv(BUF_SIZE - 1)

            if not data:
                print("server recv: connection closed")
                break

            msg = data.decode()
            print(f"message [{len(data)}]:\n{msg}")

            response = f"echo: {msg}"
            cfd.sendall(response.encode())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            cfd.close()
        except:
            pass
        
        sfd.close()

server()
