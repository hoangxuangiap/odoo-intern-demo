"""ĐOẠN CODE CHO SẴN (chậm) và PHIÊN BẢN TỐI ƯU để thực tập sinh đo và so sánh.

Cách đo bằng profiler của Odoo: bật Developer mode › biểu tượng con bọ (Debug) › "Start profiling"
› thao tác (vd. mở danh sách đối tác có cột perf_total_sales_slow) › Stop › mở kết quả (speedscope).
"""
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ❌ CHẬM: compute không store + search BÊN TRONG vòng lặp -> N+1 query
    perf_total_sales_slow = fields.Float(compute='_compute_perf_total_sales_slow')
    # ✅ NHANH: 1 truy vấn _read_group cho cả danh sách
    perf_total_sales_fast = fields.Float(compute='_compute_perf_total_sales_fast')

    def _compute_perf_total_sales_slow(self):
        for partner in self:
            orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', '=', 'sale')])
            total = 0.0
            for order in orders:          # cộng bằng Python
                total += order.amount_total
            partner.perf_total_sales_slow = total

    def _compute_perf_total_sales_fast(self):
        totals = {}
        if self.ids:
            groups = self.env['sale.order']._read_group(
                [('partner_id', 'in', self.ids), ('state', '=', 'sale')],
                ['partner_id'], ['amount_total:sum'])
            totals = {partner.id: total for partner, total in groups}
        for partner in self:
            partner.perf_total_sales_fast = totals.get(partner.id, 0.0)

    # ---- Ba cách cùng cho ra "tổng bán hàng theo đối tác" ----
    @api.model
    def perf_totals_slow(self, partners):
        result = {}
        for partner in partners:  # ❌ search trong for
            orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', '=', 'sale')])
            result[partner.id] = sum(orders.mapped('amount_total'))
        return result

    @api.model
    def perf_totals_read_group(self, partners):
        groups = self.env['sale.order']._read_group(
            [('partner_id', 'in', partners.ids), ('state', '=', 'sale')], ['partner_id'], ['amount_total:sum'])
        result = {partner.id: 0.0 for partner in partners}
        result.update({partner.id: total for partner, total in groups})
        return result

    @api.model
    def perf_totals_sql(self, partners):
        # SQL có tham số (%s) -> an toàn trước SQL injection, KHÔNG nối chuỗi.
        self.env['sale.order'].flush_model(['partner_id', 'state', 'amount_total'])
        self.env.cr.execute(
            """SELECT partner_id, COALESCE(SUM(amount_total), 0)
                 FROM sale_order
                WHERE state = 'sale' AND partner_id IN %s
             GROUP BY partner_id""",
            (tuple(partners.ids) or (0,),),
        )
        result = {partner.id: 0.0 for partner in partners}
        result.update(dict(self.env.cr.fetchall()))
        return result
