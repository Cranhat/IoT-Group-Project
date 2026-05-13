openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem \
-subj "/C=PL/ST=DN/L=Wro/O=/OU=/CN=serv/emailAddress="
