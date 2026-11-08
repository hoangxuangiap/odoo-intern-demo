# Phần B — Bài tập cấu hình nghiệp vụ (Công ty TNHH Thiết bị Văn phòng Minh An)

| Tài liệu | Nội dung |
|---|---|
| `SOP.md` | SOP từng quy trình (B0 → B5), có chỗ chèn ảnh chụp màn hình |
| `diagrams/*.svg` | Sơ đồ luồng chứng từ Mua / Bán / Kho |
| `DEMO_15_PHUT.md` | Kịch bản demo end-to-end 15 phút |
| `VAN_DE_VA_CACH_XU_LY.md` | Danh sách vấn đề thường gặp và cách xử lý |
| `VAN_DAP_NGHIEP_VU.md` | Đáp án 5 câu vấn đáp nghiệp vụ |
| `CHECKLIST_NOP_BAI.md` | Đối chiếu yêu cầu nộp bài ↔ file/việc cần làm |

## Chạy nhanh
```bash
docker compose up --build      # tạo DB "minhan" tự động (Phần B) + DB "intern" (Phần A)
```
Đăng nhập http://localhost:8069 › chọn DB **minhan** › `admin / admin`
(hoặc `nv.muahang`, `nv.banhang`, `thukho`, `quanly` · mật khẩu `MinhAn@2026`).

Module `intern_functional_setup` tự động hóa toàn bộ B0 → B5. Có thể chạy lại từng phần:
* Menu **Settings › Technical › Minh An Setup** (Developer mode) — chọn phạm vi rồi bấm *Chạy*.
* Hoặc dòng lệnh: `FUNC_SCOPE=B3,B4 ...` (xem `scripts/functional_seed.py`).

Kết quả chạy nằm ở `reports/functional_run_report.md` (log từng bước ✔/✖) và các file Excel:
`Sales_Analysis`, `Purchase_Analysis`, `Stock_Valuation`, `Moves_History`.
