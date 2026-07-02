# Nginx config

- **nginx.conf** – HTTP only (default). Used when you run locally: `docker compose up -d --build` then open http://localhost.
- **nginx-https.conf** – HTTP → HTTPS redirect + HTTPS server; requires SSL certs (for production).

## Enabling HTTPS

### 1. Get SSL certificates (Let's Encrypt with certbot)

On the **host** (not inside Docker), with your domain pointing to the server:

```bash
# Install certbot (Ubuntu/Debian)
sudo apt update && sudo apt install -y certbot

# Obtain cert (standalone mode – stops anything on 80/443 briefly, or use webroot if Nginx is already running)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Certificates will be in:
- `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

### 2. Use the HTTPS config and mount certs

**Option A – Mount Let's Encrypt dir (recommended):**

In `docker-compose.yml`, for the `nginx` service:

- Add port: `- "443:443"`
- Add volume: `- /etc/letsencrypt:/etc/nginx/ssl:ro`  
  Then in the Nginx config use:
  - `ssl_certificate     /etc/nginx/ssl/live/yourdomain.com/fullchain.pem;`
  - `ssl_certificate_key /etc/nginx/ssl/live/yourdomain.com/privkey.pem;`

Or create a dir that only has the certs (so the config path stays `/etc/nginx/ssl/fullchain.pem`):

```bash
sudo mkdir -p /etc/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/nginx/ssl/
```

Then mount: `- /etc/nginx/ssl:/etc/nginx/ssl:ro`

**Option B – Copy certs into project (e.g. for Hostinger):**

```bash
mkdir -p nginx/ssl
# Copy fullchain.pem and privkey.pem into nginx/ssl/
```

In `docker-compose.yml` add:
- `- "443:443"`
- `- ./nginx/ssl:/etc/nginx/ssl:ro`

**Use the HTTPS config:**

In `docker-compose.yml`, change the nginx config volume from:

```yaml
- ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
```

to:

```yaml
- ./nginx/nginx-https.conf:/etc/nginx/conf.d/default.conf:ro
```

### 3. Restart Nginx

```bash
docker compose up -d nginx
```

### 4. Django

Set in `.env` so Django redirects to HTTPS and uses secure cookies:

```
SECURE_SSL_REDIRECT=true
```

`settings.example.py` already sets `SECURE_PROXY_SSL_HEADER` so Django trusts `X-Forwarded-Proto` from Nginx.

### 5. Renewal (Let's Encrypt)

Certbot certs expire after 90 days. Renew on the host:

```bash
sudo certbot renew
```

If you copied certs to `/etc/nginx/ssl/`, copy them again after renewing, then:

```bash
docker compose exec nginx nginx -s reload
```

Or use a cron job: `certbot renew --quiet && cp ... && docker compose exec nginx nginx -s reload`
