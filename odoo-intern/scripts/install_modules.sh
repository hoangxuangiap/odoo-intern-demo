#!/usr/bin/env bash
# Cài app chuẩn rồi cài TỪNG module intern_* riêng lẻ,
# module nào lỗi thì ghi lại và đi tiếp (không làm hỏng cả DB).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_CMD="${ODOO_CMD:-python3 odoo/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-odoo-local.conf}"
DB="${ODOO_DB:-intern}"
BASE_APPS="${BASE_APPS:-sale_management,purchase,stock,account,mail}"
DEMO=""; [ "${WITHOUT_DEMO:-0}" = "1" ] && DEMO="--without-demo=all"
LANGOPT=""; [ -n "${LOAD_LANG:-}" ] && LANGOPT="--load-language=${LOAD_LANG}"
LOGDIR="${LOGDIR:-$HERE/../install-logs}"; mkdir -p "$LOGDIR"

echo "=== [1] Cài các app chuẩn: $BASE_APPS"
$ODOO_CMD -c "$ODOO_CONF" -d "$DB" -i "$BASE_APPS" $DEMO $LANGOPT --stop-after-init --log-level=warn \
    > "$LOGDIR/00_base.log" 2>&1 || { echo "!!! Cài app chuẩn thất bại, xem $LOGDIR/00_base.log"; exit 1; }

FAILED=()
while read -r MOD; do
    [ -z "$MOD" ] && continue
    echo "=== Cài module: $MOD"
    if $ODOO_CMD -c "$ODOO_CONF" -d "$DB" -i "$MOD" --stop-after-init --log-level=warn > "$LOGDIR/$MOD.log" 2>&1 \
       && ! grep -qE "CRITICAL|Traceback" "$LOGDIR/$MOD.log"; then
        echo "    OK"
    else
        echo "    LỖI -> xem $LOGDIR/$MOD.log"; FAILED+=("$MOD")
    fi
done < "$HERE/modules.list"

echo "=============================================="
if [ ${#FAILED[@]} -eq 0 ]; then echo "Tất cả module đã cài thành công."; else echo "Module lỗi: ${FAILED[*]}"; exit 2; fi
