# intern_vn_amount_words
Module dùng chung: hàm `amount_to_words_vn()` và model trừu tượng `vn.amount.words` (đọc số tiền VND thành chữ).
Dùng trong QWeb: `o.env['vn.amount.words'].amount_to_words(o.amount_total, o.currency_id)`.
Được dùng lại ở Bài 2.3 (intern_purchase_report) và Bài 4.3 (intern_stock_vn_report).
**Hạn chế:** chỉ đọc phần nguyên (làm tròn), chưa đọc phần thập phân.
