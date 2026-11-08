#!/usr/bin/env bash
# Chạy trong container: lần đầu tự tạo 2 DB (intern = Phần A, minhan = Phần B), sau đó khởi động Odoo.
set -u
export ODOO_CMD="python3 /opt/odoo/odoo-bin" ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
export LOGDIR=/var/lib/odoo/install-logs REPORT_DIR=/reports

until pg_isready -h "$PGHOST" -U "$PGUSER" >/dev/null 2>&1; do echo "Đợi PostgreSQL..."; sleep 2; done
exists() { psql -h "$PGHOST" -U "$PGUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$1'" 2>/dev/null; }

if [ "${SETUP_INTERN:-1}" = "1" ] && [ "$(exists intern)" != "1" ]; then
    echo ">>> Tạo DB 'intern' (Phần A: 16 module bài tập lập trình)..."
    ODOO_DB=intern bash /opt/scripts/install_modules.sh
fi
if [ "${SETUP_FUNCTIONAL:-1}" = "1" ] && [ "$(exists minhan)" != "1" ]; then
    echo ">>> Tạo DB 'minhan' (Phần B: cấu hình nghiệp vụ Công ty Minh An)..."
    FUNC_DB=minhan bash /opt/scripts/install_functional.sh
fi
echo ">>> Odoo chạy tại http://localhost:8069  (chọn DB 'intern' hoặc 'minhan' ở màn hình đăng nhập; admin / admin)"
exec $ODOO_CMD -c "$ODOO_CONF" --db-filter='^(intern|minhan)$'
