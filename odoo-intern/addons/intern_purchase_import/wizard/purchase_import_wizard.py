import base64
import io
from collections import defaultdict

from odoo import Command, fields, models
from odoo.exceptions import UserError

try:
    import openpyxl
except ImportError:  # đã khai báo external_dependencies, đây chỉ là lưới an toàn
    openpyxl = None


class PurchaseImportWizard(models.TransientModel):
    _name = 'purchase.import.wizard'
    _description = 'Import Purchase Orders from Excel'

    file = fields.Binary(string="Excel File (.xlsx)", attachment=False)
    filename = fields.Char()
    state = fields.Selection([('upload', 'Upload'), ('error', 'Errors')], default='upload')
    error_log = fields.Text(string="Errors", readonly=True)

    # ------------------------------------------------------------------
    def _read_rows(self):
        if openpyxl is None:
            raise UserError(self.env._("The Python library 'openpyxl' is not installed."))
        if not self.file:
            raise UserError(self.env._("Please upload an Excel file."))
        try:
            workbook = openpyxl.load_workbook(io.BytesIO(base64.b64decode(self.file)), data_only=True, read_only=True)
        except Exception as exc:  # noqa: BLE001 - file hỏng/không phải xlsx
            raise UserError(self.env._("Cannot read the Excel file: %s", exc)) from exc
        rows = []
        for number, row in enumerate(workbook.active.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not any(cell not in (None, '') for cell in row):
                continue  # bỏ dòng trống
            cells = (list(row) + [None] * 4)[:4]
            rows.append((number, *cells))
        return rows

    def _validate_rows(self, rows):
        """Trả về (dòng hợp lệ, danh sách lỗi theo từng dòng). Tra cứu NCC/SP theo lô để tránh N+1 query."""
        partners = {p.ref: p for p in self.env['res.partner'].search(
            [('ref', 'in', [str(r[1]).strip() for r in rows if r[1]])])}
        products = {p.default_code: p for p in self.env['product.product'].search(
            [('default_code', 'in', [str(r[2]).strip() for r in rows if r[2]])])}
        valid, errors = [], []
        for number, vendor_code, product_code, qty, price in rows:
            problems = []
            vendor = partners.get(str(vendor_code).strip()) if vendor_code else None
            product = products.get(str(product_code).strip()) if product_code else None
            if not vendor:
                problems.append(self.env._("vendor code '%s' not found", vendor_code or ''))
            if not product:
                problems.append(self.env._("product code '%s' not found", product_code or ''))
            try:
                qty_value = float(qty)
                if qty_value <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                qty_value = None
                problems.append(self.env._("quantity must be a positive number"))
            price_value = None
            if price not in (None, ''):
                try:
                    price_value = float(price)
                    if price_value < 0:
                        raise ValueError
                except (TypeError, ValueError):
                    problems.append(self.env._("price must be a non-negative number"))
            if problems:
                errors.append(self.env._("Row %(row)s: %(problems)s", row=number, problems='; '.join(problems)))
            else:
                valid.append((vendor, product, qty_value, price_value))
        return valid, errors

    def action_import(self):
        self.ensure_one()
        rows = self._read_rows()
        if not rows:
            raise UserError(self.env._("The file has no data rows (row 1 is the header)."))
        valid, errors = self._validate_rows(rows)
        if errors:  # all-or-nothing: có lỗi thì không tạo gì cả
            self.write({'state': 'error', 'error_log': '\n'.join(errors)})
            return {'type': 'ir.actions.act_window', 'res_model': self._name, 'res_id': self.id,
                    'view_mode': 'form', 'target': 'new'}
        by_vendor = defaultdict(list)
        for vendor, product, qty, price in valid:
            values = {'product_id': product.id, 'product_qty': qty}
            if price is not None:
                values['price_unit'] = price
            by_vendor[vendor].append(Command.create(values))
        orders = self.env['purchase.order'].create(
            [{'partner_id': vendor.id, 'order_line': lines} for vendor, lines in by_vendor.items()])
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._("Imported Purchase Orders"),
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', orders.ids)],
        }
