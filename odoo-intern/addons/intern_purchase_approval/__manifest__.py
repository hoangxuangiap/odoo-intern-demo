{
    'name': 'Intern - Purchase Multi-level Approval',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Multi-level approval of purchase orders based on the order amount',
    'description': """
Bài 2.1 - Phê duyệt PO nhiều cấp
================================
* Dưới ngưỡng 1: xác nhận bình thường.
* Từ ngưỡng 1 đến ngưỡng 2: cần Trưởng phòng mua duyệt.
* Trên ngưỡng 2: cần Giám đốc duyệt.
* Ngưỡng cấu hình trong Settings (lưu ở ir.config_parameter).
* Từ chối bắt buộc nhập lý do (wizard), lý do ghi vào chatter.
* Tự tạo activity cho người có quyền duyệt.
    """,
    'author': 'Intern',
    'depends': ['purchase'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/purchase_order_reject_wizard_views.xml',
        'views/purchase_order_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
