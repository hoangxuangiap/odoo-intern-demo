from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestInternApi(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = cls.env['intern.api.service']
        cls.product = cls.env['product.product'].create({
            'name': 'API Product', 'default_code': 'API-001', 'is_storable': True, 'list_price': 100})
        cls.partner = cls.env['res.partner'].create({'name': 'API Customer', 'ref': 'API-CUST'})
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.env['stock.quant']._update_available_quantity(cls.product, cls.warehouse.lot_stock_id, 7)

    def test_get_stock(self):
        result = self.service.get_stock('API-001', self.warehouse.code)
        self.assertEqual(result['stock'][0]['on_hand'], 7)
        with self.assertRaises(UserError):
            self.service.get_stock('NOPE')

    def test_create_sale_order_and_delivery_status(self):
        data = self.service.create_sale_order(
            partner_ref='API-CUST', lines=[{'default_code': 'API-001', 'qty': 2}], external_ref='WEB-1', confirm=True)
        self.assertEqual(data['state'], 'sale')
        status = self.service.get_delivery_status(data['name'])
        self.assertEqual(status['order'], data['name'])
        self.assertTrue(status['pickings'])

    def test_validation_errors(self):
        with self.assertRaises(UserError):
            self.service.create_sale_order(partner_ref='API-CUST', lines=[])
        with self.assertRaises(UserError):
            self.service.create_sale_order(partner_ref='API-CUST', lines=[{'default_code': 'API-001', 'qty': 0}])
