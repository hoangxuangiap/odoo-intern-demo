#!/usr/bin/env bash
# Nâng cấp module sau khi sửa code:  ./scripts/update_modules.sh intern_purchase_approval
set -u
ODOO_CMD="${ODOO_CMD:-python3 odoo/odoo-bin}"; ODOO_CONF="${ODOO_CONF:-odoo-local.conf}"; DB="${ODOO_DB:-intern}"
$ODOO_CMD -c "$ODOO_CONF" -d "$DB" -u "${1:?tên module hoặc danh sách cách nhau dấu phẩy}" --stop-after-init
