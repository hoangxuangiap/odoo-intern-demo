# intern_sale_tier_discount (Bài 3.2)
**Mục đích:** trên sản phẩm khai báo bảng bậc (từ số lượng X -> chiết khấu Y%). Dòng SO tự áp chiết khấu khi đổi số lượng (override `_compute_discount`).
**Cách dùng:** form sản phẩm › tab Tier Discount. **Test:** `./scripts/run_tests.sh intern_sale_tier_discount`.
**Hạn chế:** so sánh theo số lượng nhập trên dòng (chưa quy đổi đơn vị tính); với sản phẩm có bậc, chiết khấu tính theo bậc và thay thế chiết khấu chuẩn.
