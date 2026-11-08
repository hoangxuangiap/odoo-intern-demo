# intern_stock_no_negative (Bài 4.4)
**Mục đích:** không cho validate phiếu xuất/chuyển nội bộ nếu tồn tại vị trí nguồn không đủ, trừ khi kho bật `Allow Negative Stock` (thêm boolean vào `stock.warehouse`).
**Cách dùng:** Inventory › Configuration › Warehouses › bật "Allow Negative Stock" nếu cần cho phép âm.
**Hạn chế:** kiểm tra theo tồn thực (on hand) của vị trí nguồn, chưa xét riêng từng lô/serial.
