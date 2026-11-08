# intern_purchase_approval (Odoo 19)

## Mục đích
Phê duyệt đơn mua hàng (PO) nhiều cấp theo tổng tiền:

| Tổng tiền PO | Ai duyệt |
|---|---|
| < 50 triệu | Không cần duyệt |
| 50 – 200 triệu | Trưởng phòng mua |
| > 200 triệu | Giám đốc |

Hai ngưỡng chỉnh được ở **Settings › Purchase › Multi-level PO Approval**.

## Cài đặt
1. Thêm thư mục module vào `addons_path`.
2. Apps › Update Apps List › cài **Intern - Purchase Multi-level Approval**.
   Hoặc: `./odoo-bin -d <db> -i intern_purchase_approval --stop-after-init`

## Cách dùng
1. Gán group *Purchase Department Head* / *Purchase Director* cho user (Settings › Users).
2. NV mua tạo RFQ rồi bấm **Confirm Order**.
3. Nếu vượt ngưỡng, PO sang **To Approve**, người duyệt nhận activity.
4. Người duyệt bấm **Approve** hoặc **Reject** (bắt buộc nhập lý do, lý do ghi vào chatter).

## Chạy test
`./odoo-bin -d <db_test> -i intern_purchase_approval --test-enable --test-tags /intern_purchase_approval --stop-after-init`

## Hạn chế đã biết
* Logic 1 cấp/2 cấp chuẩn của Odoo (`po_double_validation`) bị thay thế bởi module này.
* Tài khoản Administrator được gán Giám đốc mặc định (để thử nghiệm).
* Activity gửi cho mọi user đủ cấp duyệt (kể cả cấp cao hơn).
* File dịch `vi_VN.po` là bản khởi đầu: nên Export lại từ Settings › Translations.
