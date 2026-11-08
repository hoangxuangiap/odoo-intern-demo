from odoo import fields, models


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Sales Commission'
    _order = 'date desc, id desc'

    _move_user_uniq = models.Constraint(
        'UNIQUE(move_id, user_id)',
        'A commission was already generated for this invoice and salesperson.',
    )

    move_id = fields.Many2one('account.move', string="Invoice", required=True, ondelete='cascade', index=True)
    user_id = fields.Many2one('res.users', string="Salesperson", required=True, index=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    basis = fields.Selection([('revenue', 'Revenue'), ('profit', 'Profit')], required=True)
    base_amount = fields.Monetary(string="Base Amount", currency_field='currency_id')
    percent = fields.Float(string="Commission (%)")
    amount = fields.Monetary(string="Commission", currency_field='currency_id')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
