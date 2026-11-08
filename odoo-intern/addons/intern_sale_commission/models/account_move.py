from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_payment_state(self):
        super()._compute_payment_state()
        # Hóa đơn bán hàng vừa chuyển sang "paid" -> sinh hoa hồng (idempotent, không tạo trùng)
        paid = self.filtered(lambda m: m.id and m.move_type == 'out_invoice' and m.payment_state == 'paid')
        if paid:
            paid._intern_generate_commissions()

    def _intern_generate_commissions(self):
        Commission = self.env['sale.commission'].sudo()
        Rule = self.env['sale.commission.rule'].sudo()
        for move in self:
            user = move.invoice_user_id
            if not user:
                continue
            rule = Rule.search([('user_id', '=', user.id), ('company_id', '=', move.company_id.id)], limit=1)
            if not rule:
                continue
            if Commission.search_count([('move_id', '=', move.id), ('user_id', '=', user.id)]):
                continue
            revenue = move.amount_untaxed_signed  # tiền tệ công ty
            cost = sum(
                line.product_id.with_company(move.company_id).standard_price * line.quantity
                for line in move.invoice_line_ids if line.product_id
            )
            base, amount = rule._compute_commission(revenue, cost)
            Commission.create({
                'move_id': move.id, 'user_id': user.id, 'date': move.invoice_date or move.date,
                'basis': rule.basis, 'base_amount': base, 'percent': rule.percent, 'amount': amount,
                'company_id': move.company_id.id,
            })
