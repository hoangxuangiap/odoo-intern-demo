# SOP — Quy trình cấu hình & vận hành (Odoo 19)

> Quy ước: **Menu** viết theo giao diện tiếng Anh (tiếng Việt tương ứng ở ngoặc).
> `[ẢNH: …]` = vị trí chèn ảnh chụp màn hình (bạn tự chụp khi thực hiện thủ công hoặc sau khi chạy script;
> script `intern_functional_setup` đã tạo sẵn toàn bộ dữ liệu để chụp).

---
## B0. Thiết lập ban đầu
### B0.1 Thông tin công ty
**Menu:** Settings › Companies (Công ty) › *Update Info*.
1. Điền Tên: *Công ty TNHH Thiết bị Văn phòng Minh An*; Địa chỉ Hà Nội; Quốc gia Việt Nam; **Tax ID (MST)**; Logo.
2. Currency = **VND** (Settings › Accounting › Currencies: kích hoạt VND trước).
3. Múi giờ: Preferences (avatar) › Timezone = `Asia/Ho_Chi_Minh`. Ngôn ngữ: Settings › Languages › Add *Vietnamese* › Preferences › Language.
`[ẢNH: form công ty]` `[ẢNH: Preferences timezone/language]`
**Lưu ý:** phải đặt quốc gia VN trước khi cài Accounting để Odoo nạp bảng tài khoản Việt Nam (TT200).

### B0.2 Người dùng & phân quyền
**Menu:** Settings › Users & Companies › Users › New.
| User | Quyền cần gán |
|---|---|
| nv.muahang | Purchase = User |
| nv.banhang | Sales = User: Own Documents Only |
| thukho | Inventory = User |
| quanly | Purchase / Sales / Inventory = Administrator |
Thêm Invoicing (Billing) cho nv.muahang, nv.banhang, quanly để tạo hóa đơn. Đăng nhập thử từng user (cửa sổ ẩn danh) và kiểm tra menu hiển thị.
`[ẢNH: form user + quyền]` `[ẢNH: màn hình sau khi đăng nhập nv.banhang]`

### B0.3 Cấu hình chung
- Inventory › Configuration › Settings: bật **Units of Measure**, **Variants** (Sales/Inventory), **Storage Locations**, **Multi-Step Routes**, **Lots & Serial Numbers**. Sales › Settings: bật **Pricelists**.
- Accounting › Configuration › Taxes: tạo/kiểm tra **GTGT 8%** và **GTGT 10%**, mỗi loại cho *Sales* và *Purchase*.
`[ẢNH: Settings đã tick]` `[ẢNH: danh sách thuế]`

---
## B1. Dữ liệu gốc
### B1.1 Danh mục sản phẩm
Inventory › Configuration › Product Categories: *Thiết bị điện tử* (con: *Máy in*, *Laptop*), *Văn phòng phẩm*, *Nội thất*.
Costing Method: Điện tử = **FIFO**, Văn phòng phẩm = **Average Cost (AVCO)**. `[ẢNH: cây danh mục + costing]`

### B1.2 Sản phẩm (≥10)
Inventory › Products › New. Cho mỗi sản phẩm: ảnh, Internal Reference, Barcode, giá bán/giá vốn, **Tracking** (Serial cho Laptop & Máy in, Lot cho Giấy A4).
- *Giấy A4*: UoM bán = Ram, UoM mua = Thùng (1 thùng = 5 ram).
- *Bút bi*: UoM = Cây, mua theo Hộp (20 cây).
- *Ghế xoay*: thuộc tính Màu (Đen/Xám) → 2 biến thể.
- *Dịch vụ lắp đặt*: Product Type = Service.
- Tab *Purchase*: thêm NCC, giá, **Delivery Lead Time**.
`[ẢNH: form Laptop]` `[ẢNH: form Giấy A4 với UoM]` `[ẢNH: biến thể ghế]`

### B1.3 Đối tác
Contacts › New. 3 NCC (1 NCC nước ngoài đặt *Vendor Currency* = USD); 5 khách hàng có **Công ty mẹ** và **Contacts & Addresses** (người liên hệ). Tab *Sales & Purchase*: **Payment Terms** (Immediate / 30 Days / 50% đầu + 50% sau 30 ngày — tạo ở Accounting › Configuration › Payment Terms).

### B1.4 Bảng giá
Sales › Products › Pricelists: *Giá bán lẻ* (giá niêm yết); *Giá đại lý*: rule 1 = giảm 10% tất cả; rule 2 = Giấy A4, Min qty 50, giảm 15%. Gán *Giá đại lý* cho 2 khách (tab Sales & Purchase › Pricelist).

---
## B2. Cấu hình kho
### B2.1 Cấu trúc kho
Inventory › Configuration › Warehouses: *Kho Hà Nội* (HN), *Kho Hồ Chí Minh* (HCM). Locations: trong `HN/Stock` tạo *Khu A (Điện tử)* (con: Kệ A-01, A-02) và *Khu B (Văn phòng phẩm)*.
### B2.2 Tồn đầu kỳ
Inventory › Operations › **Physical Inventory**: nhập 5 laptop (mỗi serial 1 dòng), 100 ram giấy (2 lot: 60 + 40), 500 bút bi → *Apply*.
### B2.3 Nhập/xuất nhiều bước
Warehouse HN: Incoming Shipments = *2 steps (Input + Stock)*; Outgoing = *2 steps (Pick + Ship)*. Quan sát chứng từ HN/IN, HN/INT, HN/PICK, HN/OUT.
### B2.4 Putaway Rules
Inventory › Configuration › Putaway Rules: *Thiết bị điện tử* → Khu A; *Văn phòng phẩm* → Khu B (When product arrives in `HN/Stock`).
### B2.5 Chuyển kho nội bộ
Inventory › Operations › Transfers › New (Operation Type = Internal Transfers HN): 20 ram giấy `HN/Stock` → `HCM/Stock` → Validate. Kiểm tra tồn từng kho ở Inventory › Reporting › Stock.
### B2.6 Kiểm kê
Physical Inventory: bút bi đếm thiếu 3, giấy thừa 1 ram → Apply. Xem bút toán: Accounting › Journal Entries (journal *Stock Valuation*) — Nợ/Có tài khoản chênh lệch kiểm kê.
### B2.7 Tái đặt hàng tự động
Inventory › Operations › Replenishment: tạo rule Giấy A4 Min 30 / Max 150 / Trigger *Auto*. Xuất kho xuống dưới 30 → Inventory › Operations › Run Scheduler → Purchase › RFQ có RFQ mới (số lượng = Max − dự báo).
`[ẢNH: rule Min/Max]` `[ẢNH: RFQ tự sinh]`

---
## B3. Nghiệp vụ mua hàng
| Bài | Thao tác chính | Kết quả cần chụp |
|---|---|---|
| B3.1 | Purchase › New RFQ (10 laptop @ 18tr) › *Send by Email* › *Confirm Order* › *Receive Products* (nhập serial) › *Create Bill* › *Register Payment* | RFQ→PO, phiếu IN/INT, bill đã thanh toán |
| B3.2 | PO 200 ram; ở phiếu IN nhập 120 → *Validate* → *Create Backorder*; lần 2 nhận 80 | 2 phiếu IN, PO nhận 200/200 |
| B3.3 | PO 10 **thùng** giấy (đổi UoM trên dòng PO) | Tồn giấy +50 ram |
| B3.4 | Từ phiếu nhập đã Done › *Return* 2 máy in; hóa đơn NCC › *Credit Note* | phiếu trả, Vendor Credit Note |
| B3.5 | Product › Purchase › *Control Policy* = *On received quantities*; thử *Create Bill* khi chưa nhận → báo lỗi "no invoiceable line" | thông báo lỗi; bill tạo được sau khi nhận |
| B3.6 | NCC USD; Accounting › Currencies › Rates: 1 USD = 25.400 VND; PO USD → nhận hàng → xem giá vốn VND | PO bằng USD, giá vốn quy đổi |
| B3.7 | Tạo 2 RFQ cho cùng sản phẩm, liên kết *Alternatives* (Compare Product Lines), chọn NCC rẻ hơn; hoặc Purchase › Orders › Blanket Orders | so sánh giá, PO được chọn |

## B4. Nghiệp vụ bán hàng
| Bài | Thao tác chính |
|---|---|
| B4.1 | Quotation › *Send by Email* › *Confirm* › Delivery (PICK rồi OUT) › *Create Invoice* › *Register Payment* |
| B4.2 | Báo giá 60 ram cho KH đại lý → đơn giá giảm 15% (63.750 so với 75.000) |
| B4.3 | SO có dòng Laptop + *Dịch vụ lắp đặt*; thêm *Optional Products* (chuột, túi) ở tab Optional Products |
| B4.4 | Đặt 10, kho còn 7 → giao 7 → *Create Backorder*; Product *Invoicing Policy = Delivered quantities* → hóa đơn 7 máy |
| B4.5 | Từ phiếu giao Done › *Return* 1 ghế; Invoice › *Credit Note* (qty 1) |
| B4.6 | SO 100tr › *Create Invoice* › *Down payment (percentage) 30%* › thu tiền; giao hàng; *Create Invoice* (Regular) → hóa đơn cuối đã trừ cọc |
| B4.7 | Users › nv.banhang.hcm › *Default Warehouse* = Kho HCM; gán khách TP.HCM cho Salesperson này (hoặc chọn Warehouse trên SO › Other Info) |

## B5. Tình huống tổng hợp
- **Case 1 MTO/Dropship:** Product › Inventory › Routes: *Replenish on Order (MTO)* + *Buy* (hoặc *Dropship*). Xác nhận SO → PO tự sinh (xem Purchase › RFQ có Source Document = SO).
- **Case 2 Truy xuất:** Inventory › Products › Lots/Serial Numbers › chọn serial › **Traceability**: thấy NCC, PO, ngày nhập, khách nhận.
- **Case 3 Một tháng:** tối thiểu 5 PO, 8 SO, 2 chuyển kho, 1 kiểm kê, 1 trả hàng mỗi chiều. Xuất báo cáo: Sales › Reporting › Sales; Purchase › Reporting › Purchase; Inventory › Reporting › Valuation; Inventory › Reporting › Moves History (Export › Excel).
