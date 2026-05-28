openssl genrsa -out client0.key 2048

openssl req -new -key client0.key -out client0.csr -subj "/C=PL/ST=DN/L=Wroc/O=../OU=../CN=.." -passout pass:IoT-p

openssl x509 -req -in client0.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out client0.crt -days 365 -sha256

