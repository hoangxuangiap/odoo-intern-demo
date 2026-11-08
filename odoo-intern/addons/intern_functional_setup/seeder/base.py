"""Hàm tiện ích dùng chung. Mọi truy cập field/model "có thể đổi tên giữa các bản Odoo" đều đi qua
has()/vals()/first_field() để script KHÔNG crash: field không tồn tại sẽ bị bỏ qua và ghi log cảnh báo."""
import base64
import io
import logging
import unicodedata

from odoo import Command, fields
from odoo.exceptions import UserError

_logger = logging.getLogger('intern.functional')


class SeederBase:

    def __init__(self, env, commit=False, report_dir=None):
        ctx = dict(env.context, tracking_disable=True, mail_notrack=True, mail_create_nolog=True,
                   no_reset_password=True, mail_activity_quick_update=True)
        self.env = env(context=ctx)
        self.commit = commit
        self.report_dir = report_dir
        self.notes = []
        self.results = []
        self.cache = {}

    # ---------------------------------------------------------------- log
    def log(self, message):
        self.notes.append(str(message))
        _logger.info(message)

    # ------------------------------------------------- field/model helpers
    def has(self, model, field=None):
        if model not in self.env:
            return False
        return field is None or field in self.env[model]._fields

    def first_field(self, model, *names):
        for name in names:
            if name in self.env[model]._fields:
                return name
        return None

    def vals(self, model, values):
        """Lọc bỏ key không phải field của model (phiên bản Odoo khác nhau) và ghi log."""
        known = self.env[model]._fields
        missing = [k for k in values if k not in known]
        if missing:
            self.log(f"⚠ {model}: bỏ qua field không có ở phiên bản này: {', '.join(missing)}")
        return {k: v for k, v in values.items() if k in known}

    def get_or_create(self, model, domain, values):
        record = self.env[model].search(domain, limit=1)
        if record:
            return record
        create_vals = {leaf[0]: leaf[2] for leaf in domain if leaf[1] == '='}
        create_vals.update(values)
        return self.env[model].create(self.vals(model, create_vals))

    def ref(self, xmlid):
        return self.env.ref(xmlid, raise_if_not_found=False)

    def currency(self, code):
        cur = self.env['res.currency'].with_context(active_test=False).search([('name', '=', code)], limit=1)
        if cur and not cur.active:
            cur.active = True
        return cur

    def uom_field(self, model):
        """Tên field đơn vị tính: product_uom_id (Odoo 19) hoặc product_uom (<= 18)."""
        return self.first_field(model, 'product_uom_id', 'product_uom')

    # -------------------------------------------------------- data helpers
    def prod(self, code):
        product = self.env['product.product'].search([('default_code', '=', code)], limit=1)
        if not product:
            raise UserError(f"Không tìm thấy sản phẩm mã '{code}'. Hãy chạy bước B1.2 trước.")
        return product

    def partner(self, ref):
        partner = self.env['res.partner'].search([('ref', '=', ref)], limit=1)
        if not partner:
            raise UserError(f"Không tìm thấy đối tác mã '{ref}'. Hãy chạy bước B1.3 trước.")
        return partner

    @property
    def company(self):
        return self.ref('base.main_company') or self.env.company

    @property
    def hn(self):
        return self.env['stock.warehouse'].search([('code', '=', 'HN')], limit=1) or self._raise('Chưa có kho HN (B2.1).')

    @property
    def hcm(self):
        return self.env['stock.warehouse'].search([('code', '=', 'HCM')], limit=1) or self._raise('Chưa có kho HCM (B2.1).')

    def _raise(self, message):
        raise UserError(message)

    def onhand(self, product, location):
        return product.with_context(location=location.id).qty_available

    # --------------------------------------------------------------- misc
    @staticmethod
    def fold(text):
        text = unicodedata.normalize('NFKD', text.replace('đ', 'd').replace('Đ', 'D'))
        return ''.join(c for c in text if not unicodedata.combining(c))

    def img(self, text, color='#1b6ca8', size=(512, 512)):
        """Ảnh PNG minh họa (base64) tạo bằng Pillow - dùng làm ảnh sản phẩm/logo."""
        try:
            from PIL import Image, ImageDraw
            image = Image.new('RGB', size, color)
            draw = ImageDraw.Draw(image)
            draw.rectangle([12, 12, size[0] - 12, size[1] - 12], outline='white', width=5)
            words, lines, current = self.fold(text).upper().split(), [], ''
            for word in words:
                if len(current) + len(word) > 16:
                    lines.append(current.strip())
                    current = ''
                current += word + ' '
            lines.append(current.strip())
            y = size[1] // 2 - 14 * len(lines)
            for line in lines:
                draw.text((size[0] // 2 - 4 * len(line), y), line, fill='white')
                y += 28
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as exc:  # noqa: BLE001 - ảnh chỉ là phần phụ
            self.log(f'⚠ Không tạo được ảnh minh họa: {exc}')
            return False

    @staticmethod
    def ean13(base12):
        digits = [int(c) for c in base12]
        total = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits))
        return base12 + str((10 - total % 10) % 10)
