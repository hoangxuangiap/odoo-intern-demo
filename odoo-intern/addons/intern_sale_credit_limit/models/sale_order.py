from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

WARNING_RATIO = 0.8  # cảnh báo khi đạt 80% hạn mức
GROUP_MANAGER = 'sales_team.group_sale_manager'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('waiting_approval', 'Waiting Credit Approval')],
        ondelete={'waiting_approval': 'set default'},
    )
    credit_warning = fields.Char(compute='_compute_credit_warning')

    # ------------------------------------------------------------------
    def _get_credit_data(self):
        """Trả về (hạn mức, công nợ hiện tại, tổng sau khi thêm đơn này) - tiền tệ công ty."""
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        company = self.company_id or self.env.company
        amount = self.amount_total
        if self.currency_id and self.currency_id != company.currency_id:
            amount = self.currency_id._convert(
                amount, company.currency_id, company, self.date_order or fields.Date.today())
        debt = partner._intern_get_debt() if partner.id else 0.0
        return partner.intern_credit_limit, debt, debt + amount

    def _is_credit_exceeded(self):
        self.ensure_one()
        limit, _debt, total = self._get_credit_data()
        return limit > 0 and total > limit

    @api.depends('partner_id', 'amount_total', 'state')
    def _compute_credit_warning(self):
        for order in self:
            order.credit_warning = False
            if not order.partner_id or order.state not in ('draft', 'sent', 'waiting_approval'):
                continue
            limit, debt, total = order._get_credit_data()
            if limit <= 0:
                continue
            company_currency = (order.company_id or self.env.company).currency_id
            fmt = lambda value: format_amount(self.env, value, company_currency)  # noqa: E731
            if total > limit:
                order.credit_warning = self.env._(
                    "Credit limit exceeded: debt %(debt)s + this order = %(total)s > limit %(limit)s. "
                    "Confirming will send the order for approval.",
                    debt=fmt(debt), total=fmt(total), limit=fmt(limit))
            elif total >= WARNING_RATIO * limit:
                order.credit_warning = self.env._(
                    "Close to credit limit: debt %(debt)s + this order = %(total)s of limit %(limit)s.",
                    debt=fmt(debt), total=fmt(total), limit=fmt(limit))

    # ------------------------------------------------------------------
    def action_confirm(self):
        blocked = self.env['sale.order']
        if not self.env.context.get('credit_approved'):
            blocked = self.filtered(lambda o: o.state in ('draft', 'sent') and o._is_credit_exceeded())
        if blocked:
            blocked.write({'state': 'waiting_approval'})
            for order in blocked:
                limit, debt, total = order._get_credit_data()
                order.message_post(body=self.env._(
                    "Credit limit exceeded (limit %(limit)s, debt after this order %(total)s). "
                    "Order sent for approval.", limit=round(limit, 2), total=round(total, 2)))
                managers = self.env['res.users'].sudo().search([('share', '=', False)]).filtered(
                    lambda u: u.has_group(GROUP_MANAGER))
                for manager in managers:
                    order.activity_schedule(
                        'mail.mail_activity_data_todo', user_id=manager.id,
                        summary=self.env._("Credit approval needed"))
        return super(SaleOrder, self - blocked).action_confirm()

    def _check_can_approve_credit(self):
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError(self.env._("Only Sales Managers can approve or refuse credit exceptions."))

    def action_approve_credit(self):
        self._check_can_approve_credit()
        orders = self.filtered(lambda o: o.state == 'waiting_approval')
        orders.write({'state': 'draft'})
        orders.message_post(body=self.env._("Credit exception approved by %s.", self.env.user.name))
        orders.with_context(credit_approved=True).action_confirm()
        orders.sudo().activity_unlink(['mail.mail_activity_data_todo'])
        return True

    def action_refuse_credit(self):
        self._check_can_approve_credit()
        orders = self.filtered(lambda o: o.state == 'waiting_approval')
        orders.write({'state': 'draft'})
        orders.message_post(body=self.env._("Credit exception refused by %s.", self.env.user.name))
        return True
