from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseRequestReport(TransactionCase):

    def test_report_renders_with_amount_in_words(self):
        vendor = self.env['res.partner'].create({'name': 'Report Vendor'})
        product = self.env['product.product'].create({'name': 'Report Product'})
        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'order_line': [Command.create({'product_id': product.id, 'product_qty': 2, 'price_unit': 1000})],
        })
        report = self.env.ref('intern_purchase_report.action_report_purchase_request')
        html, _ = self.env['ir.actions.report']._render_qweb_html(report.report_name, po.ids)
        body = html.decode()
        self.assertIn('PHIẾU ĐỀ NGHỊ MUA HÀNG', body)
        self.assertIn('Tổng tiền bằng chữ', body)
