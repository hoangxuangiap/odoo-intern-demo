# Danh sách vấn đề thường gặp và cách xử lý

> Đây là các vấn đề **dự kiến** khi cấu hình Odoo 19 theo đề bài. Khi chạy thật, hãy bổ sung vấn đề của riêng bạn
> (nguồn: `reports/functional_run_report.md`, các dòng bắt đầu bằng ⚠ hoặc ✖).

| # | Vấn đề | Nguyên nhân | Cách xử lý |
|---|---|---|---|
| 1 | Không đổi được tiền tệ công ty sang VND | Đã có bút toán/chart khác | Dùng DB mới; đặt quốc gia VN **trước** khi cài Accounting (`scripts/install_functional.sh` làm sẵn) |
| 2 | Không thấy bảng tài khoản Việt Nam | Công ty chưa có quốc gia VN khi cài Accounting | Settings › Accounting › Fiscal Localization › chọn *Vietnam* (hoặc cài `l10n_vn`) |
| 3 | Validate phiếu báo thiếu tài khoản kho (định giá tự động) | Danh mục chưa khai tài khoản Stock Valuation/Input/Output | Product Category › Inventory Valuation: khai tài khoản, hoặc để *Manual* |
| 4 | Tạo hóa đơn NCC báo "no invoiceable line" | Policy "theo số lượng nhận" + chưa nhận hàng | Nhận hàng trước (đây chính là kết quả mong đợi của B3.5) |
| 5 | Phiếu nhập 2 bước, hàng chưa vào Stock | Mới Validate `HN/IN`, chưa Validate `HN/INT` | Validate nốt phiếu `HN/INT` |
| 6 | Putaway không đưa vào Khu A/B | Rule đặt sai *when product arrives in* | Đặt `location_in` = `HN/Stock`, áp dụng theo danh mục (gồm danh mục con) |
| 7 | Xuất serial báo không đủ tồn | Serial chưa nhập hoặc nằm ở kho khác | Kiểm tra Inventory › Reporting › Stock theo serial |
| 8 | Mua theo Thùng nhưng tồn không tăng 50 ram | UoM thùng/ram khác nhóm hoặc hệ số sai | Tạo thùng = 5 ram cùng nhóm UoM với ram |
| 9 | Tỷ giá USD không đúng | Chưa khai tỷ giá ngày giao dịch | Accounting › Currencies › USD › Rates: thêm tỷ giá cho ngày PO/nhận hàng |
| 10 | Scheduler không sinh RFQ | Sản phẩm chưa có NCC, hoặc route *Buy* chưa gán | Khai NCC ở tab Purchase; kiểm tra Route *Buy*; dự báo tồn phải < Min |
| 11 | MTO không sinh PO | Route MTO đang archived | Inventory › Configuration › Routes: bỏ lọc Archived, bật *Replenish on Order (MTO)* |
| 12 | Backorder không hiện | Bấm *No Backorder* ở wizard | Chọn *Create Backorder* khi số lượng thực < nhu cầu |
| 13 | Nhân viên bán hàng thấy hết SO | Gán *All Documents* | Gán *User: Own Documents Only* |
| 14 | Script báo ⚠ "bỏ qua field …" | Tên field khác giữa các bản 19.x | Không ảnh hưởng các bước còn lại; gửi log để chỉnh code |
| 15 | PDF thiếu header/footer | wkhtmltopdf bản không patch Qt | Cài wkhtmltopdf 0.12.6 bản patched (docs Odoo) |
