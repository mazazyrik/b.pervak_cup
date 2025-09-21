# SSL Setup with Let's Encrypt

This guide shows how to add SSL/HTTPS to your Docker application using Let's Encrypt.

## Prerequisites

**You MUST have a domain name pointing to your server IP (77.110.112.125)**

### Options to get a domain:

1. **Buy a domain** (recommended):
   - Namecheap, GoDaddy, Cloudflare, etc.
   - Point A record to your server IP

2. **Free subdomain services**:
   - DuckDNS: Get `yourapp.duckdns.org` for free
   - No-IP: Free subdomain service
   - Freenom: Free domain names

3. **Example with DuckDNS**:
   ```bash
   # Go to https://www.duckdns.org/
   # Sign up and create a subdomain like "bpcup"
   # Point it to your IP: 77.110.112.125
   # Your domain will be: bpcup.duckdns.org
   ```

## Setup Steps

1. **Get your domain** and point it to `77.110.112.125`

2. **Update environment variables**:
   ```bash
   # Edit .env file
   nano .env
   
   # Change DOMAIN to your actual domain:
   DOMAIN=bpcup.duckdns.org  # or your real domain
   ```

3. **Run the SSL initialization**:
   ```bash
   # Replace with your domain and email
   ./init-letsencrypt.sh bpcup.duckdns.org your@email.com
   ```

4. **Start the SSL-enabled application**:
   ```bash
   docker compose -f docker-compose.ssl.yml up -d
   ```

## Files Created

- `docker-compose.ssl.yml` - SSL-enabled Docker Compose
- `nginx.ssl.conf` - SSL-enabled Nginx configuration
- `init-letsencrypt.sh` - SSL certificate setup script
- `certbot/` - Certificate storage directory

## Certificate Renewal

Certificates auto-renew every 12 hours via the certbot container.

## Testing

After setup, test your SSL:
- Visit `https://your-domain.com`
- Check SSL rating: https://www.ssllabs.com/ssltest/

## Troubleshooting

1. **Domain not pointing**: Verify DNS with `nslookup your-domain.com`
2. **Port 80/443 blocked**: Check firewall settings
3. **Certificate issues**: Check logs with `docker logs bpc-certbot`

## Without Domain (Development Only)

If you don't have a domain, you can use self-signed certificates for development:

```bash
# Create self-signed certificate (browsers will show warning)
mkdir -p certbot/conf/live/localhost
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certbot/conf/live/localhost/privkey.pem \
  -out certbot/conf/live/localhost/fullchain.pem \
  -subj "/CN=localhost"

# Update nginx.ssl.conf to use localhost instead of YOUR_DOMAIN
sed -i 's/YOUR_DOMAIN/localhost/g' nginx.ssl.conf
```
