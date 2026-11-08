import logging

from odoo import http
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

# Odoo 19 đổi tên kiểu route 'json' -> 'jsonrpc'; chọn tự động theo phiên bản đang chạy.
JSON_ROUTE = 'jsonrpc' if 'jsonrpc' in getattr(http, '_dispatchers', {}) else 'json'


def _authenticate():
    """Xác thực bằng API key: header 'Authorization: Bearer <key>' hoặc 'X-API-Key: <key>'.
    Key tạo ở: Preferences › Account Security › New API Key."""
    headers = request.httprequest.headers
    auth = headers.get('Authorization', '')
    key = auth[7:].strip() if auth.lower().startswith('bearer ') else headers.get('X-API-Key', '').strip()
    if not key:
        raise AccessDenied("Missing API key")
    uid = request.env['res.users.apikeys'].sudo()._check_credentials(scope='rpc', key=key)
    if not uid:
        raise AccessDenied("Invalid API key")
    request.update_env(user=uid)  # từ đây mọi truy vấn chạy với quyền của user sở hữu key


def _call(method, **kwargs):
    try:
        _authenticate()
        return {'status': 'ok', 'data': getattr(request.env['intern.api.service'], method)(**kwargs)}
    except AccessDenied as exc:
        return {'status': 'error', 'code': 401, 'message': str(exc)}
    except UserError as exc:
        return {'status': 'error', 'code': 400, 'message': str(exc)}
    except TypeError as exc:  # tham số thiếu/sai
        return {'status': 'error', 'code': 400, 'message': f"Invalid parameters: {exc}"}


class InternApiController(http.Controller):

    @http.route('/intern/api/v1/stock', type=JSON_ROUTE, auth='public', methods=['POST'])
    def stock(self, default_code=None, warehouse_code=None, **kwargs):
        return _call('get_stock', default_code=default_code, warehouse_code=warehouse_code)

    @http.route('/intern/api/v1/sale_order', type=JSON_ROUTE, auth='public', methods=['POST'])
    def sale_order(self, **kwargs):
        allowed = {'partner_ref', 'partner_id', 'lines', 'external_ref', 'confirm'}
        return _call('create_sale_order', **{k: v for k, v in kwargs.items() if k in allowed})

    @http.route('/intern/api/v1/delivery_status', type=JSON_ROUTE, auth='public', methods=['POST'])
    def delivery_status(self, order_name=None, **kwargs):
        return _call('get_delivery_status', order_name=order_name)
