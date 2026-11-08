from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    reason_id = fields.Many2one('stock.inventory.reason', string="Adjustment Reason", index=True, copy=False)
