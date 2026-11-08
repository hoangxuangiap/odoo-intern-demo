#!/usr/bin/env bash
cd "$(dirname "$0")"; source venv/bin/activate
exec python odoo/odoo-bin -c odoo-local.conf --db-filter='^(intern|minhan)$' "$@"
