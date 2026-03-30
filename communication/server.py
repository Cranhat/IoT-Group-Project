import socket

HOST = "0.0.0.0"
PORT = 3000
BACKLOG = 5
BUF_SIZE = 1024

def server():
    try:
        sfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Server socket = {sfd.fileno()}")

        sfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sfd.bind((HOST, PORT))

        sfd.listen(BACKLOG)
        print("server: waiting to connect...")

        cfd, addr = sfd.accept()
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
