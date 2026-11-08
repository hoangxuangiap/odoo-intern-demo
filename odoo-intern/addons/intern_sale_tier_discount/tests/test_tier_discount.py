from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestTierDiscount(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Tier Customer'})
        cls.product = cls.env['product.product'].create({
            'name': 'Tier Product', 'list_price': 100,
            'discount_tier_ids': [
                Command.create({'min_qty': 10, 'discount': 5}),
                Command.create({'min_qty': 50, 'discount': 10}),
            ],
        })
        cls.plain_product = cls.env['product.product'].create({'name': 'Plain Product', 'list_price': 100})

    def _line(self, product, qty):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({'product_id': product.id, 'product_uom_qty': qty})],
        })
        return order.order_line

    def test_tier_lookup(self):
        tmpl = self.product.product_tmpl_id
        self.assertEqual(tmpl._get_tier_discount(1), 0)
        self.assertEqual(tmpl._get_tier_discount(10), 5)
        self.assertEqual(tmpl._get_tier_discount(49), 5)
        self.assertEqual(tmpl._get_tier_discount(50), 10)
        self.assertEqual(tmpl._get_tier_discount(500), 10)

    def test_discount_applied_on_create(self):
        self.assertEqual(self._line(self.product, 5).discount, 0)
        self.assertEqual(self._line(self.product, 12).discount, 5)
        self.assertEqual(self._line(self.product, 60).discount, 10)

    def test_discount_follows_quantity_changes(self):
        line = self._line(self.product, 5)
        line.product_uom_qty = 20
        self.assertEqual(line.discount, 5)
        line.product_uom_qty = 100
        self.assertEqual(line.discount, 10)
        line.product_uom_qty = 3
        self.assertEqual(line.discount, 0)

    def test_product_without_tiers_unaffected(self):
        self.assertEqual(self._line(self.plain_product, 100).discount, 0)
