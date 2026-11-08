from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

MONTHS = [(str(i), name) for i, name in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'], start=1)]


class PurchaseBudget(models.Model):
    _name = 'purchase.budget'
    _description = 'Purchase Budget'
    _order = 'year desc, month desc, category_id'

    _budget_uniq = models.Constraint(
        'UNIQUE(category_id, year, month, company_id)',
        'A budget already exists for this category and month.',
    )

    category_id = fields.Many2one('product.category', string="Product Category", required=True, index=True)
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    month = fields.Selection(MONTHS, required=True, default=lambda self: str(fields.Date.today().month))
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    amount = fields.Monetary(string="Budget", required=True, currency_field='currency_id')
    spent_amount = fields.Monetary(string="Committed", compute='_compute_spent', currency_field='currency_id')
    remaining_amount = fields.Monetary(string="Remaining", compute='_compute_spent', currency_field='currency_id')

    def _get_period(self):
        self.ensure_one()
        start = datetime.combine(fields.Date.today().replace(year=self.year, month=int(self.month), day=1), time.min)
        return start, start + relativedelta(months=1)

    def _get_spent(self):
        """Tổng tiền các PO đã xác nhận của danh mục trong tháng (1 truy vấn _read_group)."""
        self.ensure_one()
        start, end = self._get_period()
        domain = [
            ('order_id.state', 'in', ('purchase', 'done')),
            ('order_id.company_id', '=', self.company_id.id),
            ('order_id.date_order', '>=', start),
            ('order_id.date_order', '<', end),
            ('product_id.categ_id', '=', self.category_id.id),
        ]
        result = self.env['purchase.order.line']._read_group(domain, aggregates=['price_subtotal:sum'])
        return (result[0][0] or 0.0) if result else 0.0

    @api.depends('category_id', 'year', 'month', 'amount', 'company_id')
    def _compute_spent(self):
        for budget in self:
            spent = budget._get_spent() if budget.id else 0.0
            budget.spent_amount = spent
            budget.remaining_amount = budget.amount - spent
