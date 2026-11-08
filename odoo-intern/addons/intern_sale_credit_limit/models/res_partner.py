from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Tên intern_credit_limit (không phải credit_limit) để KHÔNG đụng field credit_limit
    # có sẵn của module account trong Odoo 17+.
    intern_credit_limit = fields.Float(string="Credit Limit", help="0 = không giới hạn")
    intern_credit_debt = fields.Float(string="Current Debt", compute='_compute_intern_credit_debt')

    def _intern_get_debt(self):
        """Công nợ hiện tại = hóa đơn chưa thanh toán + SO đã xác nhận nhưng chưa xuất hóa đơn."""
        self.ensure_one()
        commercial = self.commercial_partner_id
        # sudo: nhân viên bán hàng có thể không có quyền kế toán
        invoices = self.env['account.move'].sudo().search([
            ('commercial_partner_id', '=', commercial.id),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ])
        invoice_debt = sum(invoices.mapped('amount_residual_signed'))  # hóa đơn +, credit note -

        orders = self.env['sale.order'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('state', '=', 'sale'),
            ('invoice_status', '!=', 'invoiced'),
        ])
        uninvoiced = 0.0
        for line in orders.order_line:
            if line.display_type or not line.product_uom_qty:
                continue
            remaining_ratio = max(line.product_uom_qty - line.qty_invoiced, 0.0) / line.product_uom_qty
            uninvoiced += line.price_total * remaining_ratio
        return invoice_debt + uninvoiced

    def _compute_intern_credit_debt(self):
        for partner in self:
            partner.intern_credit_debt = partner._intern_get_debt() if partner.id else 0.0
