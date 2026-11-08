# intern_sale_commission (Bài 3.3)
**Mục đích:** `sale.commission.rule` (nhân viên, %, tính trên doanh thu hoặc lợi nhuận). Khi hóa đơn bán chuyển sang *Paid* (override `_compute_payment_state`) tự sinh bản ghi `sale.commission` (không trùng). Báo cáo pivot + graph theo tháng.
**Phân quyền:** record rule: nhân viên chỉ thấy hoa hồng của mình, Sales Manager thấy tất cả.
**Cách dùng:** Sales › Configuration › Commission Rules; Sales › Reporting › Commissions.
**Hạn chế:** lợi nhuận = doanh thu chưa thuế - (giá vốn hiện tại x số lượng); không xử lý credit note/hoàn hoa hồng; test hóa đơn đầy đủ cần bảng tài khoản (chart of accounts).
