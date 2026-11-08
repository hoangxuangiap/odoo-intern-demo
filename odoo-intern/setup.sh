#!/usr/bin/env bash
# Cài đặt KHÔNG dùng Docker (Linux / macOS / WSL2). Tải Odoo 19 từ git, tạo venv, cài module.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"

if [ ! -d odoo ]; then
    echo ">>> Tải Odoo 19 từ GitHub..."
    git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git odoo
fi
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel
pip install -r odoo/requirements.txt -r requirements-extra.txt

# Quyền PostgreSQL cho user hiện tại (bỏ qua nếu đã có)
if command -v psql >/dev/null 2>&1; then
    sudo -u postgres createuser -s "$USER" 2>/dev/null || true
else
    echo "!!! Chưa có PostgreSQL. Ubuntu: sudo apt install postgresql postgresql-client libpq-dev"; exit 1
fi

cat > odoo-local.conf <<CONF
[options]
addons_path = $ROOT/odoo/addons,$ROOT/addons
http_port = 8069
admin_passwd = admin
db_user = $USER
workers = 0
CONF

export ODOO_CMD="python odoo/odoo-bin" ODOO_CONF="$ROOT/odoo-local.conf" ODOO_DB="${ODOO_DB:-intern}"
bash scripts/install_modules.sh || true
if [ "${SETUP_FUNCTIONAL:-1}" = "1" ]; then
    echo ">>> Phần B: tạo DB 'minhan' + chạy cấu hình nghiệp vụ (đặt SETUP_FUNCTIONAL=0 để bỏ qua)"
    ODOO_CMD="python odoo/odoo-bin" ODOO_CONF="$ROOT/odoo-local.conf" REPORT_DIR="$ROOT/reports" LOGDIR="$ROOT/install-logs" \
        bash scripts/install_functional.sh || true
fi
echo ">>> Xong. Chạy Odoo bằng:  ./run.sh   rồi mở http://localhost:8069  (DB: intern = Phần A, minhan = Phần B)"
