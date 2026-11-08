# intern_stock_adjust_reason (Bài 4.1)
**Mục đích:** bắt buộc chọn lý do khi *Apply* điều chỉnh tồn (`stock.quant`); lý do lưu vào `stock.move`; có báo cáo pivot/graph theo lý do.
**Cách dùng:** Inventory › Operations › Physical Inventory: nhập số đếm, chọn Reason, bấm Apply. Báo cáo: Inventory › Reporting › Adjustments by Reason.
**Hạn chế:** kiểu sửa trực tiếp cột "On Hand" (auto-apply) ở một số màn hình cũng đi qua `_apply_inventory` nên cũng đòi lý do.
