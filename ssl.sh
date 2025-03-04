#!/bin/bash

# Skrypt do instalacji i konfiguracji certyfikatu SSL dla serwera www działającego na Flasku na adresie http://srv14.mikr.us:40145/
# Autor: Zespół MIKR.US (wspierany przez AI)

# Instalacja narzędzi wymaganych do obsługi certyfikatów SSL
apt-get update
apt-get install -y software-properties-common
add-apt-repository universe
apt-get install -y certbot python3-certbot-nginx

# Pobranie informacji o serwerze www i konfiguracji
PORT=40145 # Port, na którym działa serwer www
DOMAIN="srv14.mikr.us" # Domena, dla której należy wygenerować certyfikat

# Uruchomienie procedury generowania certyfikatu SSL dla danej domeny i portu
certbot certonly --standalone --non-interactive --agree-tos --email kontakt@controlbyte.pl -d $DOMAIN --http-01-port $PORT

# Jeśli powyższe polecenie zakończyło się sukcesem, wypisz informację o sukcesie
if [ $? -eq 0 ]; then
    echo "Certyfikat SSL został pomyślnie wygenerowany dla domeny $DOMAIN na porcie $PORT."
else
    echo "Wystąpił błąd podczas generowania certyfikatu SSL dla domeny $DOMAIN na porcie $PORT."
fi
