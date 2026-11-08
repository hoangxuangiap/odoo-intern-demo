from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

# --- Hằng số dùng chung -------------------------------------------------------
APPROVAL_LEVELS = [
    ('none', 'No approval needed'),
    ('manager', 'Purchase Department Head'),
    ('director', 'Director'),
]
# Cấp càng cao thì số càng lớn -> dễ so sánh "người dùng có đủ cấp không".
LEVEL_RANK = {'none': 0, 'manager': 1, 'director': 2}

PARAM_MANAGER = 'intern_purchase_approval.manager_amount'
PARAM_DIRECTOR = 'intern_purchase_approval.director_amount'
DEFAULT_MANAGER_LIMIT = 50_000_000
DEFAULT_DIRECTOR_LIMIT = 200_000_000

GROUP_HEAD = 'intern_purchase_approval.group_purchase_dept_head'
GROUP_DIRECTOR = 'intern_purchase_approval.group_purchase_director'
ACTIVITY_TYPE = 'intern_purchase_approval.mail_activity_type_po_approval'


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_level = fields.Selection(
        APPROVAL_LEVELS,
        string="Required Approval",
        compute='_compute_approval_level',
    )
    can_approve = fields.Boolean(
        string="Can Current User Approve",
        compute='_compute_can_approve',
    )

    # ------------------------------------------------------------------
    # Tính cấp duyệt cần thiết
    # ------------------------------------------------------------------
    @api.model
    def _get_approval_limits(self):
        """Đọc 2 ngưỡng tiền từ ir.config_parameter (cấu hình ở Settings)."""
        params = self.env['ir.config_parameter'].sudo()
        manager_limit = float(params.get_param(PARAM_MANAGER, DEFAULT_MANAGER_LIMIT))
        director_limit = float(params.get_param(PARAM_DIRECTOR, DEFAULT_DIRECTOR_LIMIT))
        return manager_limit, director_limit

    def _get_amount_in_company_currency(self):
        """Quy đổi tổng tiền PO về tiền tệ công ty (VND) để so với ngưỡng."""
        self.ensure_one()
        company = self.company_id or self.env.company
        if not self.currency_id or self.currency_id == company.currency_id:
            return self.amount_total
        date = self.date_order.date() if self.date_order else fields.Date.context_today(self)
        return self.currency_id._convert(self.amount_total, company.currency_id, company, date)

    @api.depends('amount_total', 'currency_id', 'company_id', 'date_order')
    def _compute_approval_level(self):
        manager_limit, director_limit = self._get_approval_limits()
        for order in self:
            amount = order._get_amount_in_company_currency()
            if amount > director_limit:
                order.approval_level = 'director'
            elif amount >= manager_limit:
                order.approval_level = 'manager'
            else:
                order.approval_level = 'none'

    # ------------------------------------------------------------------
    # Người dùng hiện tại có quyền duyệt không?
    # ------------------------------------------------------------------
    @api.model
    def _get_user_approval_rank(self):
        # sudo()/cron/hệ thống: không chặn. Người dùng thường: xét theo group.
        if self.env.su:
            return LEVEL_RANK['director']
        user = self.env.user
        if user.has_group(GROUP_DIRECTOR):
            return LEVEL_RANK['director']
        if user.has_group(GROUP_HEAD):
            return LEVEL_RANK['manager']
        return LEVEL_RANK['none']

    def _is_approval_allowed_for_user(self):
        self.ensure_one()
        return LEVEL_RANK[self.approval_level] <= self._get_user_approval_rank()

    @api.depends('approval_level')
    @api.depends_context('uid')  # kết quả phụ thuộc vào người đang đăng nhập
    def _compute_can_approve(self):
        user_rank = self._get_user_approval_rank()
        for order in self:
            order.can_approve = LEVEL_RANK[order.approval_level] <= user_rank

    # ------------------------------------------------------------------
    # Móc vào luồng chuẩn của Odoo
    # ------------------------------------------------------------------
    def _approval_allowed(self):
        """Hook chuẩn của purchase: button_confirm gọi hàm này để biết PO có
        được xác nhận luôn không. True -> button_approve, False -> 'to approve'.
        Ta thay logic 1 cấp/2 cấp của Odoo bằng logic 3 cấp theo số tiền."""
        self.ensure_one()
        return self._is_approval_allowed_for_user()

    def button_confirm(self):
        orders_to_check = self.filtered(lambda o: o.state in ('draft', 'sent'))
        result = super().button_confirm()
        # Chỉ tạo activity cho các PO vừa bị chuyển sang "chờ duyệt" trong lần gọi này.
        orders_to_check.filtered(lambda o: o.state == 'to approve')._schedule_approval_activities()
        return result

    def button_approve(self, force=False):
        for order in self:
            if not order._is_approval_allowed_for_user():
                level = dict(order._fields['approval_level']._description_selection(self.env))
                raise UserError(self.env._(
                    "You are not allowed to approve %(order)s (%(amount)s). Required approver: %(level)s.",
                    order=order.name,
                    amount=format_amount(self.env, order.amount_total, order.currency_id),
                    level=level[order.approval_level],
                ))
        result = super().button_approve(force=force)
        # Đã duyệt -> đóng các activity "chờ duyệt" còn treo.
        self.sudo().activity_feedback([ACTIVITY_TYPE], feedback=self.env._("Order approved"))
        return result

    # ------------------------------------------------------------------
    # Activity cho người duyệt
    # ------------------------------------------------------------------
    def _get_approvers(self):
        """Các user nội bộ có đủ cấp để duyệt PO này (đơn giản, phù hợp công ty nhỏ)."""
        self.ensure_one()
        group = GROUP_DIRECTOR if self.approval_level == 'director' else GROUP_HEAD
        users = self.env['res.users'].sudo().search([('share', '=', False)])
        return users.filtered(lambda u: u.has_group(group))

    def _schedule_approval_activities(self):
        for order in self:
            summary = self.env._("Approve purchase order")
            note = self.env._(
                "%(order)s (%(amount)s) is waiting for your approval.",
                order=order.name,
                amount=format_amount(self.env, order.amount_total, order.currency_id),
            )
            for user in order._get_approvers():
                order.activity_schedule(
                    ACTIVITY_TYPE,
                    user_id=user.id,
                    summary=summary,
                    note=note,
                )

    # ------------------------------------------------------------------
    # Từ chối
    # ------------------------------------------------------------------
    def action_open_reject_wizard(self):
        """Mở wizard bắt nhập lý do. Việc từ chối thật sự nằm ở _action_reject."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._("Reject Purchase Order"),
            'res_model': 'purchase.order.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def _action_reject(self, reason):
        for order in self:
            if order.state != 'to approve':
                raise UserError(self.env._("Only orders waiting for approval can be rejected."))
            if not order._is_approval_allowed_for_user():
                raise UserError(self.env._("You are not allowed to reject %s.", order.name))
        self.write({'state': 'draft'})  # trả về RFQ để nhân viên mua sửa lại
        # Markup.join / Markup % tự escape nội dung -> an toàn trước XSS.
        reason_html = Markup('<br/>').join(reason.splitlines())
        for order in self:
            order.message_post(body=Markup("<p><b>%s</b></p><p>%s</p>") % (
                self.env._("Purchase order rejected"), reason_html,
            ))
            # Nhắn lại cho người phụ trách PO.
            if order.user_id and order.user_id != self.env.user:
                order.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=order.user_id.id,
                    summary=self.env._("Purchase order %s was rejected", order.name),
                    note=reason,
                )
        # Đóng activity chờ duyệt của những người khác.
        self.sudo().activity_feedback([ACTIVITY_TYPE], feedback=reason)
