from odoo import fields, models


class ProductDiscountTier(models.Model):
    _name = 'product.discount.tier'
    _description = 'Product Quantity Discount Tier'
    _order = 'product_tmpl_id, min_qty'

    _tier_uniq = models.Constraint(
        'UNIQUE(product_tmpl_id, min_qty)',
        'Two tiers of the same product cannot have the same minimum quantity.',
    )
    _discount_range = models.Constraint(
        'CHECK(discount >= 0 AND discount <= 100)',
        'The discount must be between 0 and 100 percent.',
    )

    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade', index=True)
    min_qty = fields.Float(string="From Quantity", required=True, default=1.0)
    discount = fields.Float(string="Discount (%)", required=True, digits='Discount')
