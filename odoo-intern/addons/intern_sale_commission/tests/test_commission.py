from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestCommission(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sales_a = new_test_user(cls.env, login='com_a', groups='base.group_user,sales_team.group_sale_salesman')
        cls.sales_b = new_test_user(cls.env, login='com_b', groups='base.group_user,sales_team.group_sale_salesman')
        cls.manager = new_test_user(cls.env, login='com_m', groups='base.group_user,sales_team.group_sale_manager')

    def test_compute_on_revenue_and_profit(self):
        rule = self.env['sale.commission.rule'].create({'user_id': self.sales_a.id, 'percent': 5, 'basis': 'revenue'})
        self.assertEqual(rule._compute_commission(1000, 600), (1000, 50.0))
        rule.basis = 'profit'
        self.assertEqual(rule._compute_commission(1000, 600), (400, 20.0))
        self.assertEqual(rule._compute_commission(500, 600), (-100, 0.0))  # lỗ -> 0

    def test_record_rule_own_commissions_only(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        if not journal:
            self.skipTest('No sales journal (no chart of accounts in this database).')
        partner = self.env['res.partner'].create({'name': 'Commission Customer'})
        for user, amount in ((self.sales_a, 10), (self.sales_b, 20)):
            move = self.env['account.move'].create(
                {'move_type': 'out_invoice', 'partner_id': partner.id, 'journal_id': journal.id})
            self.env['sale.commission'].create(
                {'move_id': move.id, 'user_id': user.id, 'basis': 'revenue', 'amount': amount})
        seen_a = self.env['sale.commission'].with_user(self.sales_a).search([])
        self.assertEqual(seen_a.user_id, self.sales_a)
        seen_manager = self.env['sale.commission'].with_user(self.manager).search([])
        self.assertGreaterEqual(len(seen_manager), 2)
