# intern_purchase_import (Bài 5.2)
**Mục đích:** wizard upload Excel (`openpyxl`) gồm mã NCC (Reference của đối tác), mã SP (Internal Reference), số lượng, giá; validate và báo lỗi theo từng dòng; hợp lệ hết thì tạo PO hàng loạt (1 PO / NCC).
**Cách dùng:** Purchase › Orders › Import POs from Excel. File mẫu: `static/sample/purchase_import_sample.xlsx`.
**Cài đặt:** cần `pip install openpyxl`.
**Hạn chế:** all-or-nothing (có 1 dòng lỗi thì không tạo PO nào); chỉ đọc sheet đầu tiên.
