# OpenVIDA

[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/kForth/OpenVIDA)
[![GitHub License](https://img.shields.io/github/license/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/blob/main/LICENSE)
[![GitHub Forks](https://img.shields.io/github/forks/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/forks)
[![GitHub Stars](https://img.shields.io/github/stars/kforth/OpenVIDA)](https://github.com/kForth/OpenVIDA/stargazers)

**OpenVIDA** is an open-source, web-based parts catalogue and document repository for the maintenance and repair of Volvo vehicles up to model year 2016.

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
   git clone https://github.com/your-username/OpenVIDA.git
   cd OpenVIDA
   ```

2. Start the development server:
   ```bash
   docker-compose up -d flask-dev
   ```

3. Open your browser and navigate to `http://localhost:5000`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

OpenVIDA &copy; 2026 Kestin Goforth

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
