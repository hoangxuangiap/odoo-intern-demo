from odoo import fields, models


class FunctionalSetupWizard(models.TransientModel):
    _name = 'functional.setup.wizard'
    _description = 'Minh An Functional Setup Wizard'

    scope = fields.Selection([
        ('all', 'Tất cả (B0 → B5 + báo cáo)'),
        ('B0', 'B0 - Thiết lập ban đầu'),
        ('B1', 'B1 - Dữ liệu gốc'),
        ('B2', 'B2 - Cấu hình kho'),
        ('B3', 'B3 - Nghiệp vụ mua hàng'),
        ('B4', 'B4 - Nghiệp vụ bán hàng'),
        ('C', 'B5 - Tình huống tổng hợp + báo cáo'),
    ], default='B0', required=True)
    log = fields.Text(readonly=True)

    def action_run(self):
        self.ensure_one()
        scope = None if self.scope == 'all' else [self.scope]
        self.log = self.env['intern.functional.setup'].run(scope=scope)
        return {'type': 'ir.actions.act_window', 'res_model': self._name, 'res_id': self.id,
                'view_mode': 'form', 'target': 'new'}
