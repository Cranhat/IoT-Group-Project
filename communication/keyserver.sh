openssl genrsa -out server.key 2048

openssl req -new -key server.key -out server.csr -subj "/C=PL/ST=DN/L=Wroc/O=../OU=../CN=serv" -passout pass:IoT-p

openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
