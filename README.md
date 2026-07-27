# <img width="48" height="48" src="openvida/static/img/favicons/favicon.svg"> OpenVIDA

[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/kForth/OpenVIDA)
[![GitHub License](https://img.shields.io/github/license/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/blob/main/LICENSE)
[![GitHub Forks](https://img.shields.io/github/forks/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/forks)
[![GitHub Stars](https://img.shields.io/github/stars/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/stargazers)

**OpenVIDA** is an open-source, web-based parts catalogue and document repository for the maintenance and repair of Volvo vehicles up to model year 2016.

## Table of Contents

- [ OpenVIDA](#-openvida)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Running Locally](#running-locally)
    - [Local Python Workflow (Without Docker)](#local-python-workflow-without-docker)
  - [Configuration](#configuration)
  - [Development](#development)
  - [Deployment](#deployment)
    - [Docker (Production)](#docker-production)
    - [Reverse Proxy (Nginx)](#reverse-proxy-nginx)
      - [1. Prevent Docker from bypassing UFW](#1-prevent-docker-from-bypassing-ufw)
      - [2. Open firewall ports](#2-open-firewall-ports)
      - [3. Install Nginx and copy the site config](#3-install-nginx-and-copy-the-site-config)
      - [4. TLS with Let's Encrypt (recommended)](#4-tls-with-lets-encrypt-recommended)
      - [5. Apply the Docker iptables change](#5-apply-the-docker-iptables-change)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- Browse OEM parts catalogues for Volvo vehicles (up to MY2016)
- Access maintenance and repair documentation
- Lightweight Flask-based web application
- Docker support for easy local development and deployment

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/kForth/OpenVIDA.git
   cd OpenVIDA
   ```

2. Create a local environment file:
   ```bash
   cp .env.example .env
   ```

   Set `VIDA_XSL_HOST_PATH` and `VIDA_DB_HOST_PATH` in `.env` to absolute host paths before starting Docker.

3. Start the development server:
   ```bash
   docker-compose up -d flask-dev
   ```

4. Open your browser and navigate to `http://localhost:5000`.

### Local Python Workflow (Without Docker)

1. Create and activate a virtual environment.
2. Install development dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```
3. Configure `.env` from `.env.example`.
4. Run the app:
   ```bash
   flask --app autoapp.py run
   ```

## Configuration

The project reads settings from environment variables. Start from `.env.example` and set at minimum:

- `DATABASE_URL`
- `SECRET_KEY`
- `VIDA_XSL_PATH`

See `.env.example` for additional supported variables.

## Development

Recommended checks before opening a PR:

```bash
ruff check openvida
mypy openvida
pytest
```

## Deployment

### Docker (Production)

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

### Reverse Proxy (Nginx)

In production, Nginx should sit in front of the container to handle TLS termination and static asset caching. The steps below are for Debian.

#### 1. Prevent Docker from bypassing UFW

By default Docker writes iptables rules directly, bypassing UFW. Disable this by editing (or creating) `/etc/docker/daemon.json`:

```json
{
    "iptables": false
}
```

#### 2. Open firewall ports

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

#### 3. Install Nginx and copy the site config

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

#### 4. TLS with Let's Encrypt (recommended)

Replace `openvida.net` with your domain:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d openvida.net
```

Certbot will update the config to redirect HTTP → HTTPS automatically.

#### 5. Apply the Docker iptables change

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

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and standards.

## License

OpenVIDA &copy; 2026 Kestin Goforth

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
