from odoo import fields, models


class SaleCommissionRule(models.Model):
    _name = 'sale.commission.rule'
    _description = 'Sales Commission Rule'

    _user_company_uniq = models.Constraint(
        'UNIQUE(user_id, company_id)',
        'This salesperson already has a commission rule in this company.',
    )
    _percent_range = models.Constraint(
        'CHECK(percent >= 0 AND percent <= 100)',
        'The commission percentage must be between 0 and 100.',
    )

    user_id = fields.Many2one('res.users', string="Salesperson", required=True, index=True)
    percent = fields.Float(string="Commission (%)", required=True)
    basis = fields.Selection(
        [('revenue', 'Revenue'), ('profit', 'Profit')], string="Computed On", required=True, default='revenue')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def _compute_commission(self, revenue, cost):
        """Trả về (cơ sở tính, số tiền hoa hồng). Lợi nhuận âm thì hoa hồng = 0."""
        self.ensure_one()
        base = revenue if self.basis == 'revenue' else revenue - cost
        return base, max(base, 0.0) * self.percent / 100.0
