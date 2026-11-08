from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user

from ..models.purchase_order import ACTIVITY_TYPE, PARAM_MANAGER


@tagged('post_install', '-at_install')
class TestPurchaseApproval(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env['res.partner'].create({'name': 'Test Vendor'})
        cls.product = cls.env['product.product'].create({'name': 'Test Product'})
        cls.buyer = new_test_user(
            cls.env, login='po_buyer',
            groups='base.group_user,purchase.group_purchase_user')
        cls.head = new_test_user(
            cls.env, login='po_head',
            groups='base.group_user,intern_purchase_approval.group_purchase_dept_head')
        cls.director = new_test_user(
            cls.env, login='po_director',
            groups='base.group_user,intern_purchase_approval.group_purchase_director')
        cls.activity_type = cls.env.ref(ACTIVITY_TYPE)

    def _create_po(self, total):
        return self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'order_line': [Command.create({
                'product_id': self.product.id,
                'product_qty': 1,
                'price_unit': total,
            })],
        })

    def _approval_activities(self, po):
        return po.activity_ids.filtered(lambda a: a.activity_type_id == self.activity_type)

    # --- Các mức tiền ------------------------------------------------------
    def test_small_order_is_confirmed_directly(self):
        po = self._create_po(10_000_000)
        self.assertEqual(po.approval_level, 'none')
        po.with_user(self.buyer).button_confirm()
        self.assertEqual(po.state, 'purchase')

    def test_medium_order_needs_department_head(self):
        po = self._create_po(100_000_000)
        self.assertEqual(po.approval_level, 'manager')
        po.with_user(self.buyer).button_confirm()
        self.assertEqual(po.state, 'to approve')
        # Activity được giao cho người có quyền duyệt
        self.assertIn(self.head, self._approval_activities(po).user_id)

    def test_large_order_needs_director(self):
        po = self._create_po(300_000_000)
        self.assertEqual(po.approval_level, 'director')
        po.with_user(self.buyer).button_confirm()
        self.assertEqual(po.state, 'to approve')
        activities_users = self._approval_activities(po).user_id
        self.assertIn(self.director, activities_users)
        self.assertNotIn(self.head, activities_users)

    # --- Quyền duyệt -------------------------------------------------------
    def test_head_can_approve_medium_and_closes_activity(self):
        po = self._create_po(100_000_000)
        po.with_user(self.buyer).button_confirm()
        po.with_user(self.head).button_approve()
        self.assertEqual(po.state, 'purchase')
        self.assertFalse(self._approval_activities(po))

    def test_head_cannot_approve_large(self):
        po = self._create_po(300_000_000)
        po.with_user(self.buyer).button_confirm()
        with self.assertRaises(UserError):
            po.with_user(self.head).button_approve()
        self.assertEqual(po.state, 'to approve')

    def test_director_can_approve_large(self):
        po = self._create_po(300_000_000)
        po.with_user(self.buyer).button_confirm()
        po.with_user(self.director).button_approve()
        self.assertEqual(po.state, 'purchase')

    def test_buyer_cannot_approve(self):
        po = self._create_po(100_000_000)
        po.with_user(self.buyer).button_confirm()
        with self.assertRaises(UserError):
            po.with_user(self.buyer).button_approve()

    # --- Từ chối -----------------------------------------------------------
    def test_reject_requires_reason_and_logs_chatter(self):
        po = self._create_po(100_000_000)
        po.with_user(self.buyer).button_confirm()

        wizard = self.env['purchase.order.reject.wizard'].with_user(self.head).create({
            'order_id': po.id, 'reason': '   ',
        })
        with self.assertRaises(ValidationError):
            wizard.action_confirm()

        wizard.reason = 'Price is too high'
        wizard.action_confirm()
        self.assertEqual(po.state, 'draft')
        self.assertTrue(any('Price is too high' in (m.body or '') for m in po.message_ids))

    # --- Ngưỡng cấu hình ---------------------------------------------------
    def test_threshold_is_configurable(self):
        self.env['ir.config_parameter'].sudo().set_param(PARAM_MANAGER, '5000000')
        po = self._create_po(10_000_000)
        self.assertEqual(po.approval_level, 'manager')
