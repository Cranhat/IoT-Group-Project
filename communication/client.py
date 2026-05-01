import socket
import sys
import ssl

PORT = 3000
BUF_SIZE = 99

def client():
    host = input("input sever ip:")
    ctx = ssl.create_default_context()
#    ctx.load_verify_locations("ca.pem")
    ctx.verify_mode = ssl.CERT_NONE

    try:
        addr_info = socket.getaddrinfo(host, PORT, socket.AF_INET, socket.SOCK_STREAM)

        sfd = None

        for entry in addr_info:
            family, socktype, proto, canonname, sockaddr = entry

            try:
                sfd = socket.socket(family, socktype, proto)
                print(f"Server socket = {sfd.fileno()}")

                sfd.connect(sockaddr)
                sfd = ctx.wrap_socket(sfd, server_hostname=host)

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
                mesg += "\n"
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
