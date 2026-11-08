from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('lot_id')
    def _onchange_lot_id_expiry_warning(self):
        """Khi giao hàng (outgoing) mà chọn lô đã hết hạn -> hiện cảnh báo."""
        lot = self.lot_id
        if lot and lot.expiry_date and lot.expiry_date < fields.Date.context_today(self) \
                and self.picking_code == 'outgoing':
            return {'warning': {
                'title': self.env._("Expired lot"),
                'message': self.env._("Lot %(lot)s expired on %(date)s. Are you sure you want to deliver it?",
                                      lot=lot.name, date=lot.expiry_date),
            }}
