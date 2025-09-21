#!/bin/bash

# Initialize Let's Encrypt for your domain
# Usage: ./init-letsencrypt.sh your-domain.com your@email.com

if [ $# -lt 2 ]; then
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2
RSA_KEY_SIZE=4096
DATA_PATH="./certbot"

# Create directory structure
mkdir -p "$DATA_PATH/conf"
mkdir -p "$DATA_PATH/www"

# Check if certificate already exists
if [ -d "$DATA_PATH/conf/live/$DOMAIN" ]; then
    echo "Certificate for $DOMAIN already exists. Skipping..."
    exit 0
fi

# Download recommended TLS parameters
echo "### Downloading recommended TLS parameters ..."
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"

# Create dummy certificate for initial nginx start
echo "### Creating dummy certificate for $DOMAIN ..."
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
docker run --rm -v "$PWD/$DATA_PATH/conf:/etc/letsencrypt" certbot/certbot \
    sh -c "mkdir -p /etc/letsencrypt/live/$DOMAIN && \
    openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'"

# Update nginx config with actual domain
sed "s/YOUR_DOMAIN/$DOMAIN/g" nginx.ssl.conf > nginx.ssl.conf.tmp
mv nginx.ssl.conf.tmp nginx.ssl.conf

echo "### Starting nginx ..."
docker compose -f docker-compose.ssl.yml up -d nginx

echo "### Deleting dummy certificate for $DOMAIN ..."
docker run --rm -v "$PWD/$DATA_PATH/conf:/etc/letsencrypt" certbot/certbot \
    delete --cert-name $DOMAIN --non-interactive

echo "### Requesting Let's Encrypt certificate for $DOMAIN ..."
docker compose -f docker-compose.ssl.yml run --rm certbot \
    certbot certonly --webroot -w /var/www/certbot \
    --email $EMAIL \
    -d $DOMAIN \
    --agree-tos \
    --no-eff-email \
    --force-renewal

echo "### Reloading nginx ..."
docker compose -f docker-compose.ssl.yml exec nginx nginx -s reload

echo "### SSL setup complete! Your site is now available at https://$DOMAIN"
