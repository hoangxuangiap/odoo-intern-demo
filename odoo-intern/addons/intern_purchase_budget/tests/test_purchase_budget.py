from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestPurchaseBudget(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = fields.Date.today()
        cls.category = cls.env['product.category'].create({'name': 'Budget Test Category'})
        cls.product = cls.env['product.product'].create({'name': 'Budget Product', 'categ_id': cls.category.id})
        cls.vendor = cls.env['res.partner'].create({'name': 'Budget Vendor'})
        cls.budget = cls.env['purchase.budget'].create({
            'category_id': cls.category.id, 'year': today.year, 'month': str(today.month), 'amount': 1000,
        })
        cls.buyer = new_test_user(cls.env, login='bud_buyer', groups='base.group_user,purchase.group_purchase_user')
        cls.boss = new_test_user(cls.env, login='bud_boss',
                                 groups='base.group_user,intern_purchase_budget.group_budget_override')

    def _po(self, total):
        return self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_qty': 1, 'price_unit': total})],
        })

    def test_within_budget_is_confirmed(self):
        po = self._po(500)
        po.with_user(self.buyer).button_confirm()
        self.assertIn(po.state, ('purchase', 'to approve'))
        self.assertAlmostEqual(self.budget.spent_amount, 500) if po.state == 'purchase' else None

    def test_over_budget_is_blocked(self):
        po = self._po(5000)
        with self.assertRaises(UserError):
            po.with_user(self.buyer).button_confirm()
        self.assertEqual(po.state, 'draft')

    def test_override_group_can_exceed(self):
        po = self._po(5000)
        po.with_user(self.boss).button_confirm()
        self.assertNotEqual(po.state, 'draft')
