# Running

This is a Python-based client-server application using mutual TLS authentication (mTLS).

To run this application, you need the following TLS materials:

- CA certificate: ca.pem
- CA private key: ca.key
- Server:
  - private key: server.key
  - certificate: server.crt
- Client:
  - private key: client0.key
  - certificate: client0.crt

## How to generate needed keys

1. Generate Certificate Authority (CA)

```
./genca.sh
```

Or generate manually:

Create a private key for the CA:

```
openssl genrsa -out ca.key 4096
```

Generate a self-signed CA certificate from the private key ca.key:

```
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem
```

2. Generate Server Certificate

```
./keyserver.sh
```

Or generate manually:

Create server private key:

```
openssl genrsa -out server.key 2048
```

Create a certificate signing request (CSR):

```
openssl req -new -key server.key -out server.csr -subj "/C=PL/ST=DN/L=Wroc/O=../OU=../CN=serv" -passout pass:IoT-p
```

Sign the server certificate with CA:

```
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
```

3. Generate Client Certificate

```
./keyclient.sh
```

Or generate manually:

Create client private key:

```
openssl genrsa -out client0.key 2048
```

Create CSR:

```
openssl req -new -key client0.key -out client0.csr -subj "/C=PL/ST=DN/L=Wroc/O=../OU=../CN=.." -passout pass:IoT-p
```

Sign the client certificate:

```
openssl x509 -req -in client0.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out client0.crt -days 365 -sha256
```

### Setup script

- Make sure you have  installed:
-- OpenSSL

if you don't 

```
sudo apt install openssl
```

Then generate CA, server, and client certificates:

```
cd communication
./setup_all.sh
```

### Run the Python server:
```
python3 server.py
```

### Run the Python client:
```
python3 client.py
```

When started, the client will prompt for the server IP address:

```
input server ip:
```

Enter the IP address of the server (e.g. 127.0.0.1 for local testing).

