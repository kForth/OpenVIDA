# Getting Started

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

## Running Locally

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

## Local Python Workflow (Without Docker)

1. Create and activate a virtual environment.
2. Install development dependencies:
   ```bash
   pip install ".[dev]"
   ```
3. Configure `.env` from `.env.example`.
4. Run the app:
   ```bash
   flask --app autoapp.py run
   ```

## Configuration

The project reads settings from environment variables. Start from `.env.example` and set at minimum:

- `SECRET_KEY`
- `VIDA_HOST_DB_PATH`
- `VIDA_HOST_XSL_PATH`

See `.env.example` for additional supported variables.
