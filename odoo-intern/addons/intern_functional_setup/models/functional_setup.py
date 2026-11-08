from odoo import api, models

from ..seeder import Seeder


class FunctionalSetup(models.AbstractModel):
    _name = 'intern.functional.setup'
    _description = 'Functional Setup Runner (Part B)'

    @api.model
    def run(self, scope=None, commit=False, report_dir=None):
        """scope: list tiền tố mã bước, vd ['B0', 'B1', 'B3.1']; None = tất cả.
        commit=True (khi chạy từ odoo shell): commit sau mỗi bước để giữ tiến độ."""
        seeder = Seeder(self.env, commit=commit, report_dir=report_dir)
        return seeder.run(scope)
