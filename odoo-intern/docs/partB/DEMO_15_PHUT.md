# Demo 15 phút: Mua → Nhập kho → Bán → Giao hàng → Hóa đơn

Dùng DB **minhan** đã chạy script (mọi dữ liệu nền có sẵn). Đăng nhập `quanly`.

| Phút | Việc | Nói gì |
|---|---|---|
| 0–1 | Giới thiệu công ty Minh An, 2 kho HN/HCM, 4 user | Cấu hình nền (B0, B1) đã sẵn |
| 1–4 | **Mua**: RFQ 5 máy in Canon từ NCC001 → Confirm | RFQ → PO; giá/lead time lấy từ khai báo NCC trên sản phẩm |
| 4–6 | **Nhập kho**: phiếu `HN/IN` (nhập serial) → `HN/INT` | Nhập 2 bước; Putaway đưa vào **Khu A** |
| 6–7 | **Hóa đơn NCC** (Create Bill) | Policy "theo số lượng nhận": chưa nhận thì chưa lập được hóa đơn |
| 7–9 | **Bán**: báo giá 3 máy in cho KH001 → gửi → Confirm | Bảng giá, thuế GTGT 10% |
| 9–11 | **Giao hàng**: `HN/PICK` → `HN/OUT` | Xuất 2 bước; trừ tồn kho, tạo bút toán giá vốn (FIFO) |
| 11–13 | **Hóa đơn** + **Thu tiền** | Công nợ phải thu về 0 |
| 13–14 | Truy xuất serial (Traceability) | Từ serial thấy NCC → PO → khách |
| 14–15 | Báo cáo: Sales Analysis, Stock Valuation, Moves History | Số liệu khớp luồng vừa làm |

**Dự phòng:** nếu mạng/máy chậm, mở sẵn các chứng từ đã sinh bởi script (B3.1, B4.1) và đi qua chúng.
