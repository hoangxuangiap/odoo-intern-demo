from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestAdjustReason(TransactionCase):

    def test_reason_required_and_stored_on_move(self):
        user = new_test_user(self.env, login='adj_mgr', groups='base.group_user,stock.group_stock_manager')
        env = self.env(user=user)
        product = env['product.product'].create({'name': 'Adjust Product', 'is_storable': True})
        location = env.ref('stock.stock_location_stock')
        quant = env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': product.id, 'location_id': location.id, 'inventory_quantity': 10,
        })
        with self.assertRaises(UserError):
            quant.action_apply_inventory()

        reason = env.ref('intern_stock_adjust_reason.reason_found')
        quant.inventory_reason_id = reason
        quant.action_apply_inventory()
        move = env['stock.move'].search([('product_id', '=', product.id), ('reason_id', '!=', False)])
        self.assertEqual(move.reason_id, reason)
