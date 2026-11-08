# intern_stock_expiry (Bài 4.2)
**Mục đích:** `expiry_date` trên `stock.lot`; cron hằng ngày tìm lô còn tồn sắp hết hạn trong 30 ngày, tạo activity cho thủ kho (Inventory User) và tạo 1 email tổng hợp; onchange cảnh báo khi giao lô đã hết hạn.
**Cài đặt:** phụ thuộc `stock`, `mail`. Email cần cấu hình Outgoing Mail Server mới gửi được thật.
**Chạy thử cron:** Settings › Technical › Scheduled Actions › "Intern: Check expiring lots" › Run Manually.
**Hạn chế:** chỉ cảnh báo (không chặn) khi giao lô hết hạn.
