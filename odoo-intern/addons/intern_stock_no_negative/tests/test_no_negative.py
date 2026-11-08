from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestNoNegative(TransactionCase):

    def test_block_then_allow(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        product = self.env['product.product'].create({'name': 'Neg Product', 'is_storable': True})
        customers = self.env.ref('stock.stock_location_customers')
        picking = self.env['stock.picking'].create({
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': customers.id,
            'move_ids': [Command.create({
                'name': 'out', 'product_id': product.id, 'product_uom_qty': 5,
                'location_id': warehouse.lot_stock_id.id, 'location_dest_id': customers.id,
            })],
        })
        picking.action_confirm()
        picking.move_ids.quantity = 5   # nhập số lượng muốn xuất (tồn = 0)
        with self.assertRaises(UserError):
            picking._check_negative_stock()
        warehouse.allow_negative_stock = True
        picking._check_negative_stock()  # không còn lỗi
