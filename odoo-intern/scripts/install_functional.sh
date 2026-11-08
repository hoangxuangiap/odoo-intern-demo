#!/usr/bin/env bash
# Tạo DB SẠCH cho Phần B (mặc định tên "minhan"): quốc gia VN trước khi cài kế toán -> bảng tài khoản VN (TT200),
# cài Purchase/Sales/Inventory/Invoicing, rồi chạy toàn bộ cấu hình + kịch bản B0..B5.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_CMD="${ODOO_CMD:-python3 odoo/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-odoo-local.conf}"
DB="${FUNC_DB:-minhan}"
LOGDIR="${LOGDIR:-$HERE/../install-logs}"; mkdir -p "$LOGDIR"
export REPORT_DIR="${REPORT_DIR:-/reports}"

run() { echo "=== $*"; "$@"; }
odoo() { $ODOO_CMD -c "$ODOO_CONF" -d "$DB" --stop-after-init --log-level=warn "$@"; }

echo "=== [1/6] Khởi tạo DB $DB (không dữ liệu demo)"
odoo -i base --without-demo=all > "$LOGDIR/func_01_base.log" 2>&1 || { echo "LỖI bước 1, xem $LOGDIR/func_01_base.log"; exit 1; }

echo "=== [2/6] Đặt công ty: quốc gia Việt Nam, tiền tệ VND (trước khi cài kế toán)"
echo "
c = env.ref('base.main_company')
vnd = env['res.currency'].with_context(active_test=False).search([('name','=','VND')], limit=1)
vnd.active = True
c.write({'country_id': env.ref('base.vn').id, 'currency_id': vnd.id})
env.cr.commit()
print('Company set to VN/VND')
" > "$LOGDIR/_company.py"
echo "exec(open('$LOGDIR/_company.py').read())" | $ODOO_CMD shell -c "$ODOO_CONF" -d "$DB" --log-level=warn > "$LOGDIR/func_02_company.log" 2>&1

echo "=== [3/6] Cài Invoicing + Sales + Purchase + Inventory (kèm bảng tài khoản VN)"
odoo -i l10n_vn,account,sale_management,purchase,stock,mail > "$LOGDIR/func_03_apps.log" 2>&1 \
  || { echo "LỖI cài app chuẩn, xem $LOGDIR/func_03_apps.log"; exit 1; }
for optional in stock_dropshipping purchase_requisition; do
    echo "    (tùy chọn) $optional"
    odoo -i "$optional" > "$LOGDIR/func_03_$optional.log" 2>&1 || echo "    ⚠ bỏ qua $optional (xem log)"
done

echo "=== [4/6] Cài module intern_functional_setup"
odoo -i intern_functional_setup > "$LOGDIR/func_04_module.log" 2>&1 || { echo "LỖI, xem $LOGDIR/func_04_module.log"; exit 1; }

echo "=== [5/6] Chạy cấu hình + kịch bản B0..B5 (vài phút)"
echo "exec(open('$HERE/functional_seed.py').read())" | $ODOO_CMD shell -c "$ODOO_CONF" -d "$DB" --log-level=warn 2>&1 | tee "$LOGDIR/func_05_seed.log"

echo "=== [6/6] Xong. Mở http://localhost:8069/web/login?db=$DB (admin / admin) hoặc nv.muahang, nv.banhang, thukho, quanly / MinhAn@2026"
echo "Báo cáo chạy: $REPORT_DIR/functional_run_report.md · báo cáo Excel: $REPORT_DIR/*.xlsx"
