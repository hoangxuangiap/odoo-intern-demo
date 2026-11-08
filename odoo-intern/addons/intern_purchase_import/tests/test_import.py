import base64
import io

from odoo.tests import TransactionCase, tagged

try:
    import openpyxl
except ImportError:
    openpyxl = None


@tagged('post_install', '-at_install')
class TestPurchaseImport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if openpyxl is None:
            return
        cls.vendor = cls.env['res.partner'].create({'name': 'Import Vendor', 'ref': 'IMP-V1'})
        cls.p1 = cls.env['product.product'].create({'name': 'Imp P1', 'default_code': 'IMP-P1'})
        cls.p2 = cls.env['product.product'].create({'name': 'Imp P2', 'default_code': 'IMP-P2'})

    def _wizard(self, rows):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['Vendor', 'Product', 'Qty', 'Price'])
        for row in rows:
            sheet.append(row)
        buffer = io.BytesIO()
        workbook.save(buffer)
        return self.env['purchase.import.wizard'].create({
            'file': base64.b64encode(buffer.getvalue()), 'filename': 'po.xlsx'})

    def test_import_creates_one_po_per_vendor(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        wizard = self._wizard([['IMP-V1', 'IMP-P1', 5, 100], ['IMP-V1', 'IMP-P2', 3, None]])
        action = wizard.action_import()
        orders = self.env['purchase.order'].search(action['domain'])
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(orders.order_line), 2)
        self.assertEqual(orders.order_line[0].price_unit, 100)

    def test_errors_reported_per_row_and_nothing_created(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        before = self.env['purchase.order'].search_count([])
        wizard = self._wizard([['IMP-V1', 'IMP-P1', 5, 100], ['NOPE', 'IMP-P1', 1, 1], ['IMP-V1', 'IMP-P2', -2, 'x']])
        wizard.action_import()
        self.assertEqual(wizard.state, 'error')
        self.assertIn('Row 3', wizard.error_log)
        self.assertIn('Row 4', wizard.error_log)
        self.assertNotIn('Row 2', wizard.error_log)
        self.assertEqual(self.env['purchase.order'].search_count([]), before)
