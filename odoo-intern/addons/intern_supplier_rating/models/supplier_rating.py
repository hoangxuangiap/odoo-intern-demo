from odoo import api, fields, models

SCORES = [
    ('1', '1 - Very poor'),
    ('2', '2 - Poor'),
    ('3', '3 - Average'),
    ('4', '4 - Good'),
    ('5', '5 - Excellent'),
]


class SupplierRating(models.Model):
    _name = 'supplier.rating'
    _description = 'Supplier Rating'
    _order = 'date desc, id desc'
    _rec_name = 'partner_id'

    # Odoo 19: ràng buộc UNIQUE khai báo bằng models.Constraint (thay _sql_constraints).
    # purchase_id có thể rỗng; PostgreSQL cho phép nhiều NULL trong UNIQUE.
    _purchase_uniq = models.Constraint(
        'UNIQUE(purchase_id)',
        'Each purchase order can only be rated once.',
    )

    partner_id = fields.Many2one(
        'res.partner', string="Vendor", required=True, index=True,
        domain=[('supplier_rank', '>', 0)],  # chỉ chọn nhà cung cấp
    )
    purchase_id = fields.Many2one(
        'purchase.order', string="Purchase Order",
        domain="[('partner_id', '=?', partner_id)]",  # '=?' bỏ qua điều kiện nếu partner rỗng
    )
    quality_score = fields.Selection(SCORES, string="Quality", required=True, default='3')
    delivery_score = fields.Selection(SCORES, string="Delivery", required=True, default='3')
    price_score = fields.Selection(SCORES, string="Price", required=True, default='3')
    average_score = fields.Float(
        string="Average Score", compute='_compute_average_score', store=True, digits=(3, 2),
    )
    note = fields.Html(string="Note")
    date = fields.Date(string="Date", default=fields.Date.context_today)

    @api.depends('quality_score', 'delivery_score', 'price_score')
    def _compute_average_score(self):
        for rating in self:
            scores = [int(s) for s in (rating.quality_score, rating.delivery_score, rating.price_score) if s]
            rating.average_score = sum(scores) / len(scores) if scores else 0.0

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.partner_id = self.purchase_id.partner_id
