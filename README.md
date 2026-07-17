# OpenVIDA

[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/kForth/OpenVIDA)
[![GitHub License](https://img.shields.io/github/license/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/blob/main/LICENSE)
[![GitHub Forks](https://img.shields.io/github/forks/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/forks)
[![GitHub Stars](https://img.shields.io/github/stars/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/stargazers)

**OpenVIDA** is an open-source, web-based parts catalogue and document repository for the maintenance and repair of Volvo vehicles up to model year 2016.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Development](#development)
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

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and standards.

## License

OpenVIDA &copy; 2026 Kestin Goforth

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
