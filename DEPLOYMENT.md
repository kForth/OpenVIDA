# Deployment

This guide covers production deployment with Docker and Nginx reverse proxy setup.

## Docker (Production)

The project includes a production Docker target that serves the app via Gunicorn under Supervisord.

1. Copy and configure your environment file:
   ```bash
   cp .env.example .env
   ```
   At minimum, set `SECRET_KEY`, `VIDA_XSL_HOST_PATH`, and `VIDA_DB_HOST_PATH`.

2. Build and start the production stack:
   ```bash
   docker-compose up -d flask-prod
   ```

   This starts the `flask-prod` service (port `5000`) along with the `vida-db` SQL Server container.

3. (Optional) Start DbGate for database management:
   ```bash
   docker-compose up -d dbgate
   ```
   DbGate is accessible at `http://localhost:3005`.

## Reverse Proxy (Nginx)

In production, Nginx should sit in front of the container to handle TLS termination and static asset caching. The steps below are for Debian.

### 1. Prevent Docker from bypassing UFW

By default Docker writes iptables rules directly, bypassing UFW. Disable this by editing (or creating) `/etc/docker/daemon.json`:

```json
{
    "iptables": false
}
```

### 2. Open firewall ports

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### 3. Install Nginx and copy the site config

```bash
sudo apt update && sudo apt install -y nginx
sudo cp openvida.nginx /etc/nginx/sites-available/openvida
```

Edit the site config to adjust the `server_name` to your domain name:

```bash
sudo nano /etc/nginx/sites-available/openvida
```

Enable the site and start Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/openvida /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 4. TLS with Let's Encrypt (recommended)

Replace `openvida.net` with your domain:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d openvida.net
```

Certbot will update the config to redirect HTTP -> HTTPS automatically.

### 5. Apply the Docker iptables change

After editing `daemon.json`, flush the stale Docker rules and restart:

```bash
sudo systemctl stop docker
sudo iptables -F DOCKER
sudo iptables -F DOCKER-ISOLATION-STAGE-1
sudo iptables -F DOCKER-ISOLATION-STAGE-2
sudo iptables -F DOCKER-USER
sudo systemctl start docker
docker compose up -d flask-prod
```
