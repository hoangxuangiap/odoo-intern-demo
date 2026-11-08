from collections import defaultdict

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _check_negative_stock(self):
        for picking in self.filtered(lambda p: p.picking_type_code in ('outgoing', 'internal')):
            if picking.picking_type_id.warehouse_id.allow_negative_stock:
                continue
            required = defaultdict(float)
            for line in picking.move_line_ids:
                if line.product_id.is_storable and line.location_id.usage == 'internal':
                    required[(line.product_id, line.location_id)] += line.quantity_product_uom
            shortages = []
            for (product, location), qty in required.items():
                on_hand = product.with_context(location=location.id).qty_available
                if float_compare(on_hand, qty, precision_rounding=product.uom_id.rounding) < 0:
                    shortages.append(self.env._(
                        "%(product)s at %(location)s: need %(need)s, on hand %(have)s",
                        product=product.display_name, location=location.display_name, need=qty, have=on_hand))
            if shortages:
                raise UserError(self.env._(
                    "Not enough stock to validate %(picking)s:\n%(lines)s",
                    picking=picking.name, lines='\n'.join(shortages)))

    def button_validate(self):
        self._check_negative_stock()
        return super().button_validate()
