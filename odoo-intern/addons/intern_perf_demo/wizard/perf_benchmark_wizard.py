import time

from odoo import Command, fields, models
from odoo.exceptions import UserError


class PerfBenchmarkWizard(models.TransientModel):
    _name = 'perf.benchmark.wizard'
    _description = 'Performance Benchmark'

    partner_count = fields.Integer(string="Partners to generate", default=100)
    orders_per_partner = fields.Integer(string="Orders per partner", default=3)
    result = fields.Text(readonly=True)

    # ------------------------------------------------------------------
    def action_generate_data(self):
        """Tạo dữ liệu mẫu (đối tác PERF-xxx + SO đã xác nhận) để có gì mà đo."""
        self.ensure_one()
        product = self.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        if not product:
            raise UserError(self.env._("No sellable product found."))
        partners = self.env['res.partner'].create(
            [{'name': f'PERF-{i:04d}'} for i in range(self.partner_count)])
        orders = self.env['sale.order'].create([{
            'partner_id': partner.id,
            'order_line': [Command.create({'product_id': product.id, 'product_uom_qty': 1, 'price_unit': 100 + n})],
        } for partner in partners for n in range(self.orders_per_partner)])
        orders.action_confirm()
        self.result = self.env._("Generated %(p)s partners and %(o)s confirmed orders.",
                                 p=len(partners), o=len(orders))
        return self._reopen()

    def _measure(self, function):
        self.env.flush_all()
        self.env.invalidate_all()  # xóa cache để mỗi phép đo công bằng
        cursor = self.env.cr
        queries_before = getattr(cursor, 'sql_log_count', 0)
        start = time.perf_counter()
        value = function()
        elapsed = time.perf_counter() - start
        return value, elapsed, getattr(cursor, 'sql_log_count', 0) - queries_before

    def action_run_benchmark(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        partners = Partner.search([('name', '=like', 'PERF-%')])
        if not partners:
            raise UserError(self.env._("Generate sample data first."))
        slow, t_slow, q_slow = self._measure(lambda: Partner.perf_totals_slow(partners))
        fast, t_fast, q_fast = self._measure(lambda: Partner.perf_totals_read_group(partners))
        sql, t_sql, q_sql = self._measure(lambda: Partner.perf_totals_sql(partners))
        _c1, t_cs, q_cs = self._measure(lambda: partners.mapped('perf_total_sales_slow'))
        _c2, t_cf, q_cf = self._measure(lambda: partners.mapped('perf_total_sales_fast'))
        same = all(abs(slow[k] - fast[k]) < 0.01 and abs(slow[k] - sql[k]) < 0.01 for k in slow)
        speedup = lambda a, b: f"{a / b:.1f}x" if b else "n/a"  # noqa: E731
        self.result = (
            f"Dataset: {len(partners)} partners\n"
            f"Results identical across methods: {same}\n\n"
            f"{'Method':<34}{'Time (s)':>10}{'Queries':>9}\n"
            f"{'search() inside for-loop (SLOW)':<34}{t_slow:>10.4f}{q_slow:>9}\n"
            f"{'_read_group (1 query)':<34}{t_fast:>10.4f}{q_fast:>9}   x{speedup(t_slow, t_fast)}\n"
            f"{'parameterized SQL':<34}{t_sql:>10.4f}{q_sql:>9}   x{speedup(t_slow, t_sql)}\n"
            f"{'compute not stored, per record':<34}{t_cs:>10.4f}{q_cs:>9}\n"
            f"{'compute batched with _read_group':<34}{t_cf:>10.4f}{q_cf:>9}   x{speedup(t_cs, t_cf)}\n"
        )
        return self._reopen()

    def _reopen(self):
        return {'type': 'ir.actions.act_window', 'res_model': self._name, 'res_id': self.id,
                'view_mode': 'form', 'target': 'new'}
