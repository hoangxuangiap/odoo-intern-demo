from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom_qty')
    def _compute_discount(self):
        """Giữ logic chuẩn (super), rồi với sản phẩm CÓ cấu hình bậc thì chiết khấu = % của bậc đạt được
        (đổi số lượng -> tự tăng/giảm bậc). Sản phẩm không có bậc: không đụng."""
        super()._compute_discount()
        for line in self:
            if line.display_type or not line.product_id:
                continue
            template = line.product_id.product_tmpl_id
            if template.discount_tier_ids:
                line.discount = template._get_tier_discount(line.product_uom_qty)
