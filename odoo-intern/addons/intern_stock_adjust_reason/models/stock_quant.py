from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    inventory_reason_id = fields.Many2one('stock.inventory.reason', string="Reason", copy=False)

    def _get_inventory_fields_write(self):
        # Odoo chỉ cho ghi vài field khi ở "inventory mode"; phải khai báo thêm field của mình.
        return super()._get_inventory_fields_write() + ['inventory_reason_id']

    def _apply_inventory(self):
        changed = self.filtered(
            lambda q: not float_is_zero(q.inventory_diff_quantity, precision_rounding=q.product_uom_id.rounding))
        missing = changed.filtered(lambda q: not q.inventory_reason_id)
        if missing:
            raise UserError(self.env._(
                "Please select an adjustment reason for: %s",
                ', '.join(missing.mapped('product_id.display_name'))))
        result = super()._apply_inventory()
        changed.exists().write({'inventory_reason_id': False})  # reset cho lần kiểm kê sau
        return result

    def _get_inventory_move_values(self, *args, **kwargs):
        """Ghi lý do vào stock.move do việc điều chỉnh sinh ra."""
        values = super()._get_inventory_move_values(*args, **kwargs)
        if self.inventory_reason_id:
            values['reason_id'] = self.inventory_reason_id.id
        return values
