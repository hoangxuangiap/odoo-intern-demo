from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestExpiry(TransactionCase):

    def test_is_expired(self):
        product = self.env['product.product'].create({'name': 'Exp Product', 'tracking': 'lot', 'is_storable': True})
        today = fields.Date.today()
        old = self.env['stock.lot'].create({'name': 'OLD', 'product_id': product.id, 'expiry_date': today - timedelta(days=1)})
        new = self.env['stock.lot'].create({'name': 'NEW', 'product_id': product.id, 'expiry_date': today + timedelta(days=100)})
        self.assertTrue(old.is_expired)
        self.assertFalse(new.is_expired)

    def test_cron_creates_activity_for_storekeeper(self):
        product = self.env['product.product'].create({'name': 'Exp Product 2', 'tracking': 'lot', 'is_storable': True})
        lot = self.env['stock.lot'].create({
            'name': 'SOON', 'product_id': product.id,
            'expiry_date': fields.Date.today() + timedelta(days=10)})
        self.env['stock.quant']._update_available_quantity(
            product, self.env.ref('stock.stock_location_stock'), 5, lot_id=lot)
        self.env['stock.lot']._cron_check_expiring_lots()
        self.assertTrue(lot.activity_ids)
        count = len(lot.activity_ids)
        self.env['stock.lot']._cron_check_expiring_lots()  # chạy lại không tạo trùng
        self.assertEqual(len(lot.activity_ids), count)
