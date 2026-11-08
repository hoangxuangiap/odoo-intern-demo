from odoo import fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderRejectWizard(models.TransientModel):
    _name = 'purchase.order.reject.wizard'
    _description = 'Purchase Order Rejection Wizard'

    order_id = fields.Many2one('purchase.order', string="Purchase Order",
                               required=True, ondelete='cascade')
    reason = fields.Text(string="Reason", required=True)

    def action_confirm(self):
        self.ensure_one()
        reason = (self.reason or '').strip()
        # required=True chỉ chặn ô trống; chuỗi toàn dấu cách vẫn lọt -> kiểm tra thêm.
        if not reason:
            raise ValidationError(self.env._("Please enter a reason for the rejection."))
        self.order_id._action_reject(reason)
        return {'type': 'ir.actions.act_window_close'}
