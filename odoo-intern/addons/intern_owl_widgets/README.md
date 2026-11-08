# intern_owl_widgets (Bài 5.3)
**Widget `intern_star_rating`:** field widget OWL hiển thị điểm 1-5 dạng sao, click để chấm (áp dụng cho 3 điểm trên form Supplier Rating); dùng được cho field Selection hoặc Integer: `<field name="x" widget="intern_star_rating"/>`.
**Dashboard:** Client Action (menu "Intern Dashboard"): doanh số hôm nay, số PO chờ duyệt, số phiếu kho chờ xử lý, lấy qua `useService("orm")`.
**Hạn chế:** doanh số cộng thẳng `amount_total` (không quy đổi tiền tệ); "PO chờ duyệt" = trạng thái `to approve`.
