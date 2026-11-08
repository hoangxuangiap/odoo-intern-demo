# Đối chiếu yêu cầu nộp bài Phần B

| # | Yêu cầu | Đã có | Bạn cần làm |
|---|---|---|---|
| 1 | SOP từng quy trình có ảnh chụp màn hình | `SOP.md` (đủ nội dung bước + vị trí `[ẢNH]`) | **Chụp ảnh màn hình** theo các `[ẢNH: …]` (dữ liệu đã được script tạo sẵn) rồi chèn vào SOP |
| 2 | Sơ đồ luồng chứng từ Mua, Bán, Kho | `diagrams/luong_mua_hang.svg`, `luong_ban_hang.svg`, `luong_kho.svg` | Mở bằng trình duyệt; xuất PNG/PDF nếu cần |
| 3 | Backup database | `scripts/backup_db.sh` | Chạy `./scripts/backup_db.sh minhan` sau khi chạy script → file trong `backups/` |
| 4 | Demo 15 phút end-to-end | `DEMO_15_PHUT.md` | Luyện theo kịch bản |
| 5 | Danh sách vấn đề + cách xử lý | `VAN_DE_VA_CACH_XU_LY.md` + `reports/functional_run_report.md` | Bổ sung vấn đề thực tế bạn gặp |
| — | Vấn đáp nghiệp vụ | `VAN_DAP_NGHIEP_VU.md` | Học và tự diễn đạt lại |

## Đối chiếu bài tập ↔ bước script
B0.1 `b01_company` · B0.2 `b02_users` · B0.3 `b03_settings` · B1.1 `b11_categories` · B1.2 `b12_products` · B1.3 `b13_partners` ·
B1.4 `b14_pricelists` · B2.1 `b21_warehouses` · B2.2 `b22_opening_stock` · B2.3 `b23_routes` · B2.4 `b24_putaway` ·
B2.5 `b25_transfer` · B2.6 `b26_count` · B2.7 `b27_reorder` · B3.1–B3.7 `b31…b37` · B4.1–B4.7 `b41…b47` ·
Case 1/2/3 `c1_mto_dropship`, `c2_traceability`, `c3_month_and_reports`.
Mã nguồn: `addons/intern_functional_setup/seeder/`.
