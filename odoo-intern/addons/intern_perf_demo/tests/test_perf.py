from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPerf(TransactionCase):

    def test_three_methods_give_same_result(self):
        product = self.env['product.product'].create({'name': 'Perf Product', 'list_price': 10})
        partners = self.env['res.partner'].create([{'name': f'PERFT-{i}'} for i in range(3)])
        for index, partner in enumerate(partners):
            for _n in range(index + 1):
                self.env['sale.order'].create({
                    'partner_id': partner.id,
                    'order_line': [Command.create({'product_id': product.id, 'product_uom_qty': 1, 'price_unit': 100})],
                }).action_confirm()
        Partner = self.env['res.partner']
        slow = Partner.perf_totals_slow(partners)
        fast = Partner.perf_totals_read_group(partners)
        sql = Partner.perf_totals_sql(partners)
        for pid in partners.ids:
            self.assertAlmostEqual(slow[pid], fast[pid])
            self.assertAlmostEqual(slow[pid], sql[pid])
        self.assertEqual(partners.mapped('perf_total_sales_slow'), partners.mapped('perf_total_sales_fast'))
