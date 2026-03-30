import socket
import sys

PORT = 3000
BUF_SIZE = 99

def client():
    host = input("input sever ip:")

    try:
        addr_info = socket.getaddrinfo(host, PORT, socket.AF_INET, socket.SOCK_STREAM)

        sfd = None

        for entry in addr_info:
            family, socktype, proto, canonname, sockaddr = entry

            try:
                sfd = socket.socket(family, socktype, proto)
                print(f"Server socket = {sfd.fileno()}")

                sfd.connect(sockaddr)
                break

            except Exception as e:
                print(f"client: connect error: {e}")
                if sfd:
                    sfd.close()
                sfd = None

        if sfd is None:
            print("client: failed to connect")
            return

        while True:
            try:
                mesg = input()
                sfd.sendall(mesg.encode())

                data = sfd.recv(BUF_SIZE - 1)

                if not data:
                    print("client recv: connection closed")
                    break

                print(data.decode())

            except Exception as e:
                print(f"Error: {e}")
                break

    finally:
        if 'sfd' in locals() and sfd:
            sfd.close()

client()
