from datetime import datetime

from .base import SeederBase, _logger
from .cases import CaseMixin
from .flows import FlowMixin
from .master import MasterMixin

# (mã bước, tiêu đề, tên hàm) - chạy theo thứ tự này
STEPS = [
    ('B0.1', 'Thông tin công ty', 'b01_company'),
    ('B0.2', 'Người dùng và phân quyền', 'b02_users'),
    ('B0.3', 'Cấu hình chung + thuế GTGT', 'b03_settings'),
    ('B1.1', 'Danh mục sản phẩm', 'b11_categories'),
    ('B1.2', 'Sản phẩm (11 sản phẩm)', 'b12_products'),
    ('B1.3', 'Đối tác (3 NCC, 5 khách)', 'b13_partners'),
    ('B1.4', 'Bảng giá', 'b14_pricelists'),
    ('B2.1', 'Cấu trúc kho', 'b21_warehouses'),
    ('B2.2', 'Tồn kho đầu kỳ', 'b22_opening_stock'),
    ('B2.3', 'Nhập/xuất nhiều bước', 'b23_routes'),
    ('B2.4', 'Putaway rules', 'b24_putaway'),
    ('B2.5', 'Chuyển kho nội bộ HN → HCM', 'b25_transfer'),
    ('B2.6', 'Kiểm kê', 'b26_count'),
    ('B3.1', 'Mua hàng quy trình cơ bản', 'b31_purchase_basic'),
    ('B3.2', 'Nhận hàng một phần + backorder', 'b32_partial_receipt'),
    ('B3.3', 'Đơn vị tính mua khác bán', 'b33_uom_purchase'),
    ('B3.4', 'Trả hàng NCC + Vendor Credit Note', 'b34_vendor_return'),
    ('B3.5', 'Đối chiếu 3 bên', 'b35_three_way_match'),
    ('B3.6', 'Mua ngoại tệ (USD)', 'b36_foreign_currency'),
    ('B3.7', 'Thỏa thuận mua hàng / so sánh NCC', 'b37_tender'),
    ('B4.1', 'Bán hàng quy trình cơ bản', 'b41_sale_basic'),
    ('B4.2', 'Bảng giá đại lý', 'b42_pricelist_check'),
    ('B4.3', 'Dịch vụ và sản phẩm tùy chọn', 'b43_service_optional'),
    ('B4.4', 'Giao hàng thiếu + backorder', 'b44_short_delivery'),
    ('B4.5', 'Khách trả hàng + Credit Note', 'b45_customer_return'),
    ('B4.6', 'Đặt cọc 30%', 'b46_deposit'),
    ('B4.7', 'Bán từ kho HCM', 'b47_hcm_sale'),
    ('B2.7', 'Tái đặt hàng tự động (Min/Max)', 'b27_reorder'),
    ('C1', 'Tình huống 1: MTO / Dropship', 'c1_mto_dropship'),
    ('C2', 'Tình huống 2: Truy xuất nguồn gốc', 'c2_traceability'),
    ('C3', 'Tình huống 3: Một tháng hoạt động + báo cáo', 'c3_month_and_reports'),
]


class Seeder(MasterMixin, FlowMixin, CaseMixin, SeederBase):

    def run(self, scope=None):
        for code, title, method in STEPS:
            if scope and not any(code.startswith(prefix) for prefix in scope):
                continue
            self.notes = []
            status = 'OK'
            try:
                with self.env.cr.savepoint():
                    getattr(self, method)()
            except Exception as exc:  # noqa: BLE001 - mỗi bước độc lập, lỗi bước này không dừng bước khác
                status = 'LỖI'
                self.notes.append(f'✖ {type(exc).__name__}: {exc}')
                _logger.exception('Step %s failed', code)
            self.env.invalidate_all()
            if self.commit:
                self.env.cr.commit()
            self.results.append((code, title, status, list(self.notes)))
            print(f'[{status:>4}] {code} {title}', flush=True)
        return self.report()

    def report(self):
        ok = sum(1 for r in self.results if r[2] == 'OK')
        lines = [f'# Báo cáo chạy cấu hình Phần B - {datetime.now():%d/%m/%Y %H:%M}',
                 f'Kết quả: {ok}/{len(self.results)} bước thành công', '']
        for code, title, status, notes in self.results:
            lines.append(f'## {code} - {title}: {"✔ OK" if status == "OK" else "✖ LỖI"}')
            lines += [f'- {n}' for n in notes]
            lines.append('')
        text = '\n'.join(lines)
        try:
            path = f'{self._report_dir()}/functional_run_report.md'
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(text)
            text += f'\n(Báo cáo đã lưu: {path})'
        except Exception:  # noqa: BLE001
            pass
        return text
