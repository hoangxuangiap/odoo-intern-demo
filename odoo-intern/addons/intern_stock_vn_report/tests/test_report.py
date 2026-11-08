from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStockVnReport(TransactionCase):

    def test_receipt_report_renders(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        product = self.env['product.product'].create({'name': 'VN Report Product', 'standard_price': 1000})
        supplier_loc = self.env.ref('stock.stock_location_suppliers')
        picking = self.env['stock.picking'].create({
            'picking_type_id': warehouse.in_type_id.id,
            'location_id': supplier_loc.id,
            'location_dest_id': warehouse.lot_stock_id.id,
            'move_ids': [Command.create({
                'name': 'in', 'product_id': product.id, 'product_uom_qty': 3,
                'location_id': supplier_loc.id, 'location_dest_id': warehouse.lot_stock_id.id})],
        })
        picking.action_confirm()
        report = self.env.ref('intern_stock_vn_report.action_report_phieu_nhap_kho')
        html, _ = self.env['ir.actions.report']._render_qweb_html(report.report_name, picking.ids)
        body = html.decode()
        self.assertIn('PHIẾU NHẬP KHO', body)
        self.assertIn('01-VT', body)
