# Odoo 19 Intern Project — Phần A (lập trình) + Phần B (cấu hình nghiệp vụ)

16 module `intern_*` cho Giai đoạn 1–5, kèm cấu hình để **tự tải Odoo 19 từ GitHub** và chạy ở **http://localhost:8069**.

## Cách 1 (khuyên dùng, Windows/Mac/Linux): Docker
Cài Docker Desktop, rồi trong thư mục này:
```bash
docker compose up --build
```
- Lần đầu: build image (tải Odoo 19 từ `github.com/odoo/odoo`, nhánh 19.0), tạo DB `intern`, cài từng module (≈10–20 phút).
- Sau đó mở **http://localhost:8069** — đăng nhập `admin` / `admin`.
- Log cài module: volume `odoo-data`, thư mục `install-logs/` (xem bằng `docker compose exec odoo ls /var/lib/odoo/install-logs`).

## Cách 2: Không Docker (Linux / macOS / WSL2)
Cần: `git`, `python3.10+`, PostgreSQL (`sudo apt install postgresql libpq-dev build-essential python3-dev python3-venv libldap2-dev libsasl2-dev wkhtmltopdf`).
```bash
./setup.sh      # tải Odoo 19 từ git, tạo venv, cài thư viện, cài các module
./run.sh        # chạy Odoo -> http://localhost:8069
```

## Chạy unit test một module
```bash
./scripts/run_tests.sh intern_purchase_approval         # không Docker
docker compose exec odoo bash -c "cd /opt && ODOO_CONF=/etc/odoo/odoo.conf ODOO_CMD='python3 /opt/odoo/odoo-bin' bash /opt/scripts/run_tests.sh intern_purchase_approval"
```

## Phần B — Cấu hình nghiệp vụ (Công ty Minh An)
`docker compose up --build` cũng tự tạo DB **minhan** và chạy module `intern_functional_setup`:
cấu hình công ty VN/VND, 4 user + phân quyền, thuế GTGT, 11 sản phẩm (serial/lot/UoM/biến thể), 3 NCC + 5 khách,
bảng giá đại lý, 2 kho nhiều bước, putaway, tồn đầu kỳ, kiểm kê, Min/Max, rồi **chạy các kịch bản B3.1–B3.7, B4.1–B4.7
và 3 tình huống tổng hợp**, xuất báo cáo Excel vào thư mục `reports/`.
Đăng nhập chọn DB `minhan` (admin/admin hoặc nv.muahang, nv.banhang, thukho, quanly / `MinhAn@2026`).
Tài liệu nộp bài: **`docs/partB/`** (SOP, sơ đồ luồng, demo 15 phút, vấn đề & xử lý, vấn đáp). Backup DB: `./scripts/backup_db.sh minhan`.
Chạy lại từng phần: Developer mode › Settings › Technical › **Minh An Setup**.

## Danh sách module (Phần A)
| Giai đoạn | Bài | Module |
|---|---|---|
| 1 | 1.1 + 1.2 | `intern_supplier_rating` |
| 2 | 2.1 | `intern_purchase_approval` |
| 2 | 2.2 | `intern_purchase_budget` |
| 2 | 2.3 | `intern_purchase_report` (+ `intern_vn_amount_words` dùng chung) |
| 3 | 3.1 | `intern_sale_credit_limit` |
| 3 | 3.2 | `intern_sale_tier_discount` |
| 3 | 3.3 | `intern_sale_commission` |
| 4 | 4.1 | `intern_stock_adjust_reason` |
| 4 | 4.2 | `intern_stock_expiry` |
| 4 | 4.3 | `intern_stock_vn_report` |
| 4 | 4.4 | `intern_stock_no_negative` |
| 5 | 5.1 | `intern_api` (tài liệu: `docs/API.md`, Postman: `docs/*.json`) |
| 5 | 5.2 | `intern_purchase_import` |
| 5 | 5.3 | `intern_owl_widgets` |
| 5 | 5.4 | `intern_perf_demo` |
| — | tất cả | `intern_suite` (cài 1 lần mọi module) |
| B | Phần B | `intern_functional_setup` (DB `minhan`) |

## Sau khi sửa code
`./scripts/update_modules.sh intern_xxx` (hoặc `-u` trong Docker), rồi F5 trình duyệt.

## Tiếng Việt
Đặt `LOAD_LANG: vi_VN` trong `docker-compose.yml` (hoặc `LOAD_LANG=vi_VN ./setup.sh`) trước lần cài đầu tiên.
Mới có file `i18n/vi_VN.po` đầy đủ cho `intern_purchase_approval`; module khác hãy Export từ Settings › Translations.

## Lưu ý quan trọng
Code được viết theo chuẩn Odoo 19 nhưng **chưa được chạy thử trên Odoo 19 thật** (cả Phần A lẫn Phần B) (môi trường soạn không có mạng). Script cài đặt cài từng module riêng và ghi log lỗi ở `install-logs/<module>.log`: nếu một module báo lỗi (thường do tên view/field khác nhẹ giữa các bản 19.x), gửi log đó để sửa.
