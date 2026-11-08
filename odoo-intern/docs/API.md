# Intern API (Bài 5.1)

Base URL: `http://localhost:8069`
Xác thực: tạo **API key** (avatar › Preferences › Account Security › New API Key), gửi kèm mọi request:
`Authorization: Bearer <API_KEY>` (hoặc header `X-API-Key: <API_KEY>`). Request chạy với quyền của user sở hữu key.

Mọi endpoint: `POST`, `Content-Type: application/json`, body dạng JSON-RPC:
```json
{"jsonrpc": "2.0", "method": "call", "params": { ... }}
```
Kết quả nằm trong `result`: `{"status": "ok", "data": ...}` hoặc `{"status": "error", "code": 400|401, "message": "..."}`.

## 1. Tồn kho — `POST /intern/api/v1/stock`
Params: `default_code` (bắt buộc), `warehouse_code` (tùy chọn, bỏ trống = mọi kho).
```bash
curl -s http://localhost:8069/intern/api/v1/stock \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"default_code":"LAPTOP-DELL","warehouse_code":"WH"}}'
```
Trả về: `{"product": "...", "stock": [{"warehouse": "WH", "on_hand": 5, "forecast": 5, "available": 5}]}`

## 2. Tạo đơn bán — `POST /intern/api/v1/sale_order`
Params: `partner_ref` (Reference của khách) hoặc `partner_id`; `lines`: `[{"default_code","qty","price_unit"(tùy chọn)}]`; `external_ref` (mã đơn bên ngoài); `confirm` (true = xác nhận luôn).
Trả về: `{"id", "name", "state", "amount_total"}`.

## 3. Trạng thái giao hàng — `POST /intern/api/v1/delivery_status`
Params: `order_name` (vd `S00001`). Trả về danh sách phiếu giao: `name`, `state`, `scheduled_date`, `date_done`.

## Mã lỗi
`401` thiếu/sai API key · `400` dữ liệu không hợp lệ (không tìm thấy sản phẩm/khách, số lượng <= 0...).

## Postman
Import `docs/intern_api.postman_collection.json`, sửa biến `base_url` và `api_key`.
