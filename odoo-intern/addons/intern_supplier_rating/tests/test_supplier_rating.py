from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestSupplierRating(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env['res.partner'].create({'name': 'Rated Vendor', 'supplier_rank': 1})
        cls.product = cls.env['product.product'].create({'name': 'Rated Product'})

    def _create_po(self):
        return self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_qty': 1, 'price_unit': 10})],
        })

    def _rate(self, q='3', d='3', p='3', po=None):
        return self.env['supplier.rating'].create({
            'partner_id': self.vendor.id, 'purchase_id': po.id if po else False,
            'quality_score': q, 'delivery_score': d, 'price_score': p,
        })

    def test_average_score(self):
        self.assertAlmostEqual(self._rate('5', '4', '3').average_score, 4.0)
        self.assertAlmostEqual(self._rate('5', '5', '4').average_score, 4.67, places=2)

    def test_one_rating_per_purchase_order(self):
        po = self._create_po()
        self._rate(po=po)
        with self.assertRaises(Exception), mute_logger('odoo.sql_db'):
            self._rate(po=po)

    def test_partner_rating_stats(self):
        self._rate('5', '5', '5')
        self._rate('3', '3', '3')
        self.assertEqual(self.vendor.rating_count, 2)
        self.assertAlmostEqual(self.vendor.rating_avg, 4.0)
        action = self.vendor.action_view_supplier_ratings()
        self.assertEqual(action['domain'], [('partner_id', '=', self.vendor.id)])
