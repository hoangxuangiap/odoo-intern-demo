from datetime import timedelta

from markupsafe import Markup

from odoo import api, fields, models

WARNING_DAYS = 30
GROUP_STOREKEEPER = 'stock.group_stock_user'


class StockLot(models.Model):
    _inherit = 'stock.lot'

    expiry_date = fields.Date(string="Expiry Date")
    is_expired = fields.Boolean(compute='_compute_is_expired')

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.context_today(self)
        for lot in self:
            lot.is_expired = bool(lot.expiry_date and lot.expiry_date < today)

    @api.model
    def _cron_check_expiring_lots(self):
        """Chạy hằng ngày: lô còn tồn sắp hết hạn trong 30 ngày -> activity cho thủ kho + 1 email tổng hợp."""
        today = fields.Date.context_today(self)
        lots = self.search([
            ('expiry_date', '>=', today),
            ('expiry_date', '<=', today + timedelta(days=WARNING_DAYS)),
            ('product_qty', '>', 0),
        ], order='expiry_date')
        if not lots:
            return True
        storekeepers = self.env['res.users'].search([('share', '=', False)]).filtered(
            lambda u: u.has_group(GROUP_STOREKEEPER))
        summary = self.env._("Lot expiring soon")
        for lot in lots:
            already = lot.activity_ids.filtered(lambda a: a.summary == summary).user_id
            for user in storekeepers - already:
                lot.activity_schedule(
                    'mail.mail_activity_data_todo', user_id=user.id, summary=summary,
                    note=self.env._("Lot %(lot)s of %(product)s expires on %(date)s.",
                                    lot=lot.name, product=lot.product_id.display_name, date=lot.expiry_date),
                    date_deadline=lot.expiry_date)
        emails = ','.join(filter(None, storekeepers.mapped('email')))
        if emails:
            rows = Markup('').join(
                Markup("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>") % (
                    lot.name, lot.product_id.display_name, lot.product_qty, lot.expiry_date)
                for lot in lots)
            body = Markup(
                "<p>%s</p><table border='1' cellpadding='4' style='border-collapse:collapse'>"
                "<tr><th>Lot</th><th>Product</th><th>Qty</th><th>Expiry</th></tr>%s</table>"
            ) % (self.env._("Lots expiring within %s days:", WARNING_DAYS), rows)
            self.env['mail.mail'].sudo().create({
                'subject': self.env._("Daily expiry report"),
                'body_html': body,
                'email_to': emails,
                'auto_delete': True,
            })
        return True
