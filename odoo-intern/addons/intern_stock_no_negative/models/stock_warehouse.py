from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    allow_negative_stock = fields.Boolean(
        string="Allow Negative Stock", help="If unchecked, outgoing transfers cannot be validated without enough stock.")
