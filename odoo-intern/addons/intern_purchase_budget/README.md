# intern_purchase_budget (Bài 2.2)
**Mục đích:** ngân sách mua hàng theo danh mục sản phẩm và theo tháng; khi xác nhận PO nếu vượt ngân sách thì chặn (`UserError`), trừ nhóm *Purchase Budget Override*.
**Cài đặt:** phụ thuộc `purchase`. **Cách dùng:** Purchase › Configuration › Purchase Budgets.
**Hạn chế:** so sánh theo tiền tệ công ty (giả định PO cùng tiền tệ); chỉ khớp đúng danh mục (không tính danh mục con); tháng lấy theo ngày đặt hàng của PO.
