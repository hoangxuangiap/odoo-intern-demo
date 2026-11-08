from collections import defaultdict

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

GROUP_OVERRIDE = 'intern_purchase_budget.group_budget_override'


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _check_purchase_budget(self):
        """Kiểm tra ngân sách theo danh mục + tháng của PO. Vượt -> UserError,
        trừ khi người dùng thuộc nhóm 'Purchase Budget Override' (khi đó ghi chú vào chatter)."""
        can_override = self.env.su or self.env.user.has_group(GROUP_OVERRIDE)
        Budget = self.env['purchase.budget']
        for order in self.filtered(lambda o: o.state in ('draft', 'sent')):
            order_date = (order.date_order or fields.Datetime.now())
            totals = defaultdict(float)
            for line in order.order_line:
                if line.product_id:
                    totals[line.product_id.categ_id] += line.price_subtotal
            for category, amount in totals.items():
                budget = Budget.search([
                    ('category_id', '=', category.id),
                    ('year', '=', order_date.year),
                    ('month', '=', str(order_date.month)),
                    ('company_id', '=', order.company_id.id),
                ], limit=1)
                if not budget:
                    continue  # không có ngân sách -> không kiểm tra
                projected = budget.spent_amount + amount
                if projected <= budget.amount:
                    continue
                over = projected - budget.amount
                message = self.env._(
                    "Budget exceeded for category %(category)s (%(month)s/%(year)s): "
                    "budget %(budget)s, committed %(spent)s, this order %(amount)s, over by %(over)s.",
                    category=category.display_name, month=budget.month, year=budget.year,
                    budget=format_amount(self.env, budget.amount, budget.currency_id),
                    spent=format_amount(self.env, budget.spent_amount, budget.currency_id),
                    amount=format_amount(self.env, amount, budget.currency_id),
                    over=format_amount(self.env, over, budget.currency_id),
                )
                if not can_override:
                    raise UserError(message)
                order.message_post(body=self.env._("Budget overridden by %(user)s. %(msg)s",
                                                   user=self.env.user.name, msg=message))

    def button_confirm(self):
        self._check_purchase_budget()
        return super().button_confirm()
