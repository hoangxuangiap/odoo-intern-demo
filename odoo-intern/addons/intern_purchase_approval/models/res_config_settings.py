from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # `config_parameter` = Odoo tự đọc/ghi giá trị này vào ir.config_parameter
    # khi bấm Save ở màn hình Settings. Không cần viết get_values/set_values.
    purchase_manager_approval_amount = fields.Float(
        string="Department Head approval from",
        config_parameter='intern_purchase_approval.manager_amount',
        default=50_000_000,
    )
    purchase_director_approval_amount = fields.Float(
        string="Director approval above",
        config_parameter='intern_purchase_approval.director_amount',
        default=200_000_000,
    )

    @api.constrains('purchase_manager_approval_amount', 'purchase_director_approval_amount')
    def _check_approval_amounts(self):
        for settings in self:
            if settings.purchase_manager_approval_amount <= 0:
                raise ValidationError(self.env._("Approval thresholds must be positive."))
            if settings.purchase_director_approval_amount <= settings.purchase_manager_approval_amount:
                raise ValidationError(self.env._(
                    "The Director threshold must be greater than the Department Head threshold."
                ))
