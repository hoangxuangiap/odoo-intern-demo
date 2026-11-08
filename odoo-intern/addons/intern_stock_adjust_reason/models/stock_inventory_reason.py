from odoo import fields, models


class StockInventoryReason(models.Model):
    _name = 'stock.inventory.reason'
    _description = 'Inventory Adjustment Reason'
    _order = 'name'

    _name_uniq = models.Constraint('UNIQUE(name)', 'This reason already exists.')

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
