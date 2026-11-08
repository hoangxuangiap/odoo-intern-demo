from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_tier_ids = fields.One2many('product.discount.tier', 'product_tmpl_id', string="Quantity Discount Tiers")

    def _get_tier_discount(self, qty):
        """% chiết khấu của bậc cao nhất có min_qty <= qty (0 nếu chưa đạt bậc nào)."""
        self.ensure_one()
        matching = self.discount_tier_ids.filtered(lambda t: t.min_qty <= qty)
        return max(matching, key=lambda t: t.min_qty).discount if matching else 0.0
