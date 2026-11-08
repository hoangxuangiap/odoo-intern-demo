# intern_sale_credit_limit (Bài 3.1)
**Mục đích:** hạn mức công nợ khách hàng. Công nợ = hóa đơn chưa thanh toán + SO đã xác nhận chưa xuất hóa đơn. Vượt hạn mức -> SO chuyển `Waiting Credit Approval`, Sales Manager duyệt/từ chối. Banner cảnh báo trên form SO khi đạt 80% hạn mức.
**Cài đặt:** phụ thuộc `sale`, `account`. **Cách dùng:** form khách hàng › tab Credit Limit.
**Lưu ý:** field tên `intern_credit_limit` để không trùng `credit_limit` của module account.
**Hạn chế:** đơn chưa xuất hóa đơn tính theo tỷ lệ số lượng; quy đổi tiền tệ đơn giản.
