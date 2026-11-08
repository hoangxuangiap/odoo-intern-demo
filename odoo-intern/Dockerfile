# Odoo 19 được TẢI TỪ GIT (GitHub) ngay lúc build image.
FROM python:3.12-slim-bookworm
ARG ODOO_BRANCH=19.0
ENV LANG=C.UTF-8 DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
        libjpeg-dev zlib1g-dev libfreetype6-dev libffi-dev libssl-dev \
        postgresql-client wkhtmltopdf fonts-dejavu fonts-noto-core curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${ODOO_BRANCH} https://github.com/odoo/odoo.git /opt/odoo
RUN pip install --no-cache-dir -U pip wheel \
    && pip install --no-cache-dir -r /opt/odoo/requirements.txt openpyxl

RUN useradd -m -d /var/lib/odoo -s /bin/bash odoo \
    && mkdir -p /mnt/extra-addons /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo /opt/odoo
USER odoo
EXPOSE 8069
