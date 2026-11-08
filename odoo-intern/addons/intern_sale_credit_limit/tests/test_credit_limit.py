from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestCreditLimit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Credit Customer', 'intern_credit_limit': 1000})
        cls.product = cls.env['product.product'].create({'name': 'Credit Product', 'list_price': 100})
        cls.manager = new_test_user(cls.env, login='credit_mgr', groups='base.group_user,sales_team.group_sale_manager')

    def _so(self, price):
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_uom_qty': 1, 'price_unit': price})],
        })

    def test_under_limit_confirms(self):
        so = self._so(500)
        so.action_confirm()
        self.assertEqual(so.state, 'sale')

    def test_over_limit_is_blocked_then_approved(self):
        so = self._so(5000)
        so.action_confirm()
        self.assertEqual(so.state, 'waiting_approval')
        so.with_user(self.manager).action_approve_credit()
        self.assertEqual(so.state, 'sale')

    def test_confirmed_uninvoiced_orders_count_as_debt(self):
        self._so(800).action_confirm()
        self.assertAlmostEqual(self.partner._intern_get_debt(), 800, delta=200)  # +thuế nếu có
        so2 = self._so(500)  # 800 + 500 > 1000
        so2.action_confirm()
        self.assertEqual(so2.state, 'waiting_approval')

    def test_warning_message(self):
        so = self._so(900)
        self.assertTrue(so.credit_warning)
