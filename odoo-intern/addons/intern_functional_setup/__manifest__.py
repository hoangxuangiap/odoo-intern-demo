{
    'name': 'Intern - Functional Setup (Phần B: Công ty Minh An)',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Tự động cấu hình nghiệp vụ Phần B: công ty, user, sản phẩm, kho, mua/bán/kho, báo cáo',
    'description': """
Cấu hình nghiệp vụ (Functional) Phần B - Công ty TNHH Thiết bị Văn phòng Minh An.
Chạy toàn bộ B0..B5 bằng 1 lệnh (odoo shell) hoặc từng bước trong menu "Minh An Setup".
Mỗi bước độc lập, idempotent (chạy lại không tạo trùng), ghi log + báo cáo.
    """,
    'author': 'Intern',
    'depends': ['sale_management', 'purchase', 'stock', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/setup_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
