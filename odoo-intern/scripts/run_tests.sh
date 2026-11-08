#!/usr/bin/env bash
# Chạy unit test cho 1 module:  ./scripts/run_tests.sh intern_purchase_approval
set -u
MOD="${1:?Cú pháp: run_tests.sh <ten_module>}"
ODOO_CMD="${ODOO_CMD:-python3 odoo/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-odoo-local.conf}"
TESTDB="${ODOO_DB:-intern}_test_$MOD"
$ODOO_CMD -c "$ODOO_CONF" -d "$TESTDB" -i "sale_management,purchase,stock,account,$MOD" \
    --test-enable --test-tags "/$MOD" --stop-after-init --log-level=test
