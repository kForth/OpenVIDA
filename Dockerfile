# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-PYTHON_VERSION_NOT_SET}

FROM python:${INSTALL_PYTHON_VERSION} AS builder

WORKDIR /app

RUN true
COPY requirements requirements
RUN pip install --no-cache -r requirements/prod.txt

# COPY webpack.config.js autoapp.py ./
COPY autoapp.py ./
COPY vida_flask vida_flask
# COPY assets assets
COPY .env.example .env

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION} AS production

WORKDIR /app

RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb
RUN apt-get update && \
    apt-get install -y unixodbc && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY --from=builder --chown=sid:sid /app/vida_flask/static /app/vida_flask/static
COPY requirements requirements
RUN pip install --no-cache --user -r requirements/prod.txt
RUN pip freeze > reqs.txt

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord_programs /etc/supervisor/conf.d

COPY . .

EXPOSE 5000
ENTRYPOINT ["/bin/bash", "scripts/supervisord_entrypoint.sh"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]
