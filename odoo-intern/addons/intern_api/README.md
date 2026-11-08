# intern_api (Bài 5.1)
**Mục đích:** 3 endpoint JSON, xác thực bằng API key của Odoo: tồn kho theo mã SP & kho; tạo SO; tra cứu trạng thái giao hàng.
**Tài liệu:** xem `docs/API.md` và `docs/intern_api.postman_collection.json` ở thư mục gốc dự án.
**Cài đặt:** phụ thuộc `sale`, `stock`. Tạo API key: avatar › Preferences › Account Security › New API Key.
**Hạn chế:** kiểu route tự chọn `jsonrpc` (Odoo 19) hoặc `json`; chưa có rate limit.
