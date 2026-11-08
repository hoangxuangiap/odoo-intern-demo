"""B0 Thiết lập ban đầu · B1 Dữ liệu gốc · B2.1-B2.4 Cấu hình kho."""
from odoo import Command

COMPANY_NAME = 'Công ty TNHH Thiết bị Văn phòng Minh An'

USERS = [
    # login, tên, nhóm quyền (xmlid)
    ('nv.muahang', 'Nguyễn Văn Mua - NV mua hàng', ['purchase.group_purchase_user', 'account.group_account_invoice']),
    ('nv.banhang', 'Trần Thị Bán - NV bán hàng', ['sales_team.group_sale_salesman', 'account.group_account_invoice']),
    ('thukho', 'Lê Văn Kho - Thủ kho', ['stock.group_stock_user']),
    ('quanly', 'Phạm Quản Lý - Quản lý',
     ['purchase.group_purchase_manager', 'sales_team.group_sale_manager', 'stock.group_stock_manager',
      'account.group_account_invoice']),
]
USER_PASSWORD = 'MinhAn@2026'

# Nhóm quyền bật tính năng (tương đương tick trong Settings)
FEATURE_GROUPS = [
    ('uom.group_uom', 'Đơn vị tính (UoM)'),
    ('product.group_product_variant', 'Biến thể sản phẩm'),
    ('stock.group_stock_multi_locations', 'Storage Locations'),
    ('stock.group_adv_location', 'Multi-Step Routes'),
    ('stock.group_production_lot', 'Lot/Serial Number'),
    ('product.group_product_pricelist', 'Bảng giá (Pricelists)'),
    ('sale.group_discount_per_so_line', 'Chiết khấu trên dòng SO'),
    ('base.group_multi_currency', 'Đa tiền tệ'),
]

PRODUCTS = [
    dict(code='LAPTOP-DELL', name='Laptop Dell Latitude 5440', categ='Laptop', tracking='serial',
         cost=18_000_000, price=22_000_000, color='#34495e', invoice_policy='delivery'),
    dict(code='MAY-IN-CANON', name='Máy in Canon LBP2900', categ='Máy in', tracking='serial',
         cost=3_200_000, price=4_200_000, color='#7f8c8d'),
    dict(code='GIAY-A4', name='Giấy A4 Double A', categ='Văn phòng phẩm', tracking='lot',
         cost=62_000, price=75_000, color='#f39c12', uom='Ram', po_uom=('Thùng (5 ram)', 'Ram', 5)),
    dict(code='BUT-BI-TL', name='Bút bi Thiên Long', categ='Văn phòng phẩm', tracking='none',
         cost=3_000, price=5_000, color='#2980b9', uom='Cây', po_uom=('Hộp (20 cây)', 'Cây', 20)),
    dict(code='GHE-XOAY', name='Ghế xoay văn phòng', categ='Nội thất', tracking='none',
         cost=1_100_000, price=1_650_000, color='#27ae60', variants=True),
    dict(code='DV-LAP-DAT', name='Dịch vụ lắp đặt', categ=None, service=True, price=500_000, color='#8e44ad'),
    dict(code='CHUOT-LOGI', name='Chuột không dây Logitech M331', categ='Thiết bị điện tử', tracking='none',
         cost=180_000, price=290_000, color='#16a085'),
    dict(code='TUI-LAPTOP', name='Túi chống sốc laptop 15.6 inch', categ='Thiết bị điện tử', tracking='none',
         cost=150_000, price=250_000, color='#d35400'),
    dict(code='MAY-CHIEU-EPSON', name='Máy chiếu Epson EB-X06', categ='Thiết bị điện tử', tracking='none',
         cost=9_500_000, price=12_500_000, color='#c0392b'),
    dict(code='BAN-LAM-VIEC', name='Bàn làm việc 1m4', categ='Nội thất', tracking='none',
         cost=1_400_000, price=2_200_000, color='#6d4c41'),
    dict(code='SO-TAY-A5', name='Sổ tay bìa cứng A5', categ='Văn phòng phẩm', tracking='none',
         cost=25_000, price=40_000, color='#1abc9c'),
]

# NCC: giá mua + lead time (ngày) theo sản phẩm
SELLERS = {
    'NCC001': [('LAPTOP-DELL', 18_000_000, 7), ('MAY-IN-CANON', 3_200_000, 7), ('GHE-XOAY', 1_100_000, 5),
               ('MAY-CHIEU-EPSON', 9_500_000, 10), ('BAN-LAM-VIEC', 1_400_000, 5), ('CHUOT-LOGI', 180_000, 3),
               ('TUI-LAPTOP', 150_000, 3)],
    'NCC002': [('GIAY-A4', 310_000, 3), ('BUT-BI-TL', 60_000, 3), ('SO-TAY-A5', 25_000, 3),
               ('MAY-CHIEU-EPSON', 9_200_000, 12), ('BAN-LAM-VIEC', 1_350_000, 6)],
    'NCC003': [('LAPTOP-DELL', 700, 21)],  # USD
}

VENDORS = [
    dict(ref='NCC001', name='Công ty TNHH Phân phối Thiết bị Số Hà Nội', city='Hà Nội', term='d30'),
    dict(ref='NCC002', name='Công ty CP Văn phòng phẩm Phía Nam', city='Hồ Chí Minh', term='immediate'),
    dict(ref='NCC003', name='Dell Technologies Asia Pacific Pte Ltd', city='Singapore', country='base.sg',
         currency='USD', term='immediate'),
]
CUSTOMERS = [
    dict(ref='KH001', name='Công ty CP Công nghệ Sao Việt', city='Hà Nội', term='immediate',
         holding='Tập đoàn Sao Việt Holdings', contacts=[('Nguyễn Văn An', 'contact'), ('Trần Thị Bình', 'invoice')]),
    dict(ref='KH002', name='Công ty TNHH Xây dựng Đại Phát', city='Hà Nội', term='d30',
         holding='Tập đoàn Đại Phát', contacts=[('Lê Minh Châu', 'contact'), ('Phạm Thu Dung', 'invoice')]),
    dict(ref='KH003', name='Công ty TNHH Thương mại Hưng Thịnh', city='Hồ Chí Minh', term='split', dealer=True,
         contacts=[('Võ Quốc Em', 'contact')]),
    dict(ref='KH004', name='Công ty CP Đại lý Văn phòng phẩm Phương Nam', city='Hồ Chí Minh', term='d30', dealer=True,
         contacts=[('Đỗ Thị Giang', 'contact')]),
    dict(ref='KH005', name='Công ty CP Giáo dục Tri Thức', city='Đà Nẵng', term='immediate',
         contacts=[('Hoàng Văn Hải', 'contact')]),
]


class MasterMixin:

    # ================================================================ B0.1
    def b01_company(self):
        env = self.env
        company = self.company
        vn, vnd = self.ref('base.vn'), self.currency('VND')
        company.write(self.vals('res.company', {
            'name': COMPANY_NAME, 'street': 'Số 25 Phố Duy Tân', 'street2': 'Phường Dịch Vọng Hậu, Quận Cầu Giấy',
            'city': 'Hà Nội', 'country_id': vn.id, 'vat': '0101234567', 'phone': '+84 24 3999 8888',
            'email': 'info@minhan.vn', 'website': 'https://minhan.vn',
            'logo': self.img('Minh An Office', '#1b6ca8', (512, 256)),
        }))
        self.log(f'Công ty: {company.name} - MST {company.vat} - {company.city}')

        if company.currency_id != vnd:
            try:
                with env.cr.savepoint():
                    company.currency_id = vnd
                self.log('Tiền tệ công ty: VND')
            except Exception as exc:  # noqa: BLE001
                self.log(f'⚠ Không đổi được tiền tệ sang VND ({exc}). Dùng DB mới + scripts/install_functional.sh.')
        else:
            self.log('Tiền tệ công ty: VND ✔')

        chart = env['account.chart.template']
        if hasattr(chart, 'try_loading') and 'chart_template' in company._fields and not company.chart_template:
            try:
                with env.cr.savepoint():
                    chart.try_loading('vn', company=company, install_demo=False)
                self.log('Đã nạp hệ thống tài khoản Việt Nam (TT200).')
            except Exception as exc:  # noqa: BLE001
                self.log(f'⚠ Chưa nạp được bảng tài khoản VN: {exc}')
        else:
            self.log(f'Bảng tài khoản: {getattr(company, "chart_template", None) or "đã có"}')

        # Ngôn ngữ Tiếng Việt + múi giờ
        lang_ok = self._install_vietnamese()
        admin = self.ref('base.user_admin')
        user_vals = {'tz': 'Asia/Ho_Chi_Minh'}
        if lang_ok:
            user_vals['lang'] = 'vi_VN'
        admin.write(user_vals)
        company.partner_id.write({k: v for k, v in user_vals.items() if k in company.partner_id._fields})
        self.log(f'Múi giờ: Asia/Ho_Chi_Minh · Ngôn ngữ: {"Tiếng Việt" if lang_ok else "chưa cài được vi_VN"}')

    def _install_vietnamese(self):
        env = self.env
        lang = env['res.lang'].with_context(active_test=False).search([('code', '=', 'vi_VN')], limit=1)
        if not lang:
            return False
        try:
            with env.cr.savepoint():
                if hasattr(env['res.lang'], '_activate_lang'):
                    env['res.lang']._activate_lang('vi_VN')
                env['base.language.install'].create({'lang_ids': [Command.set(lang.ids)]}).lang_install()
        except Exception as exc:  # noqa: BLE001
            self.log(f'⚠ Cài bản dịch vi_VN lỗi: {exc}')
        return bool(env['res.lang'].search([('code', '=', 'vi_VN')]))

    # ================================================================ B0.2
    def _group_field(self):
        return self.first_field('res.users', 'group_ids', 'groups_id')

    def _make_user(self, login, name, xmlids, extra=None):
        env = self.env
        user = env['res.users'].with_context(active_test=False).search([('login', '=', login)], limit=1)
        group_ids = [g.id for g in (self.ref(x) for x in ['base.group_user'] + xmlids) if g]
        values = {'name': name, 'login': login, 'email': f'{login}@minhan.vn', 'password': USER_PASSWORD,
                  'tz': 'Asia/Ho_Chi_Minh', 'company_id': self.company.id, 'company_ids': [Command.set(self.company.ids)],
                  self._group_field(): [Command.set(group_ids)]}
        if env['res.lang'].search_count([('code', '=', 'vi_VN')]):
            values['lang'] = 'vi_VN'
        values.update(extra or {})
        if user:
            user.write(self.vals('res.users', {k: v for k, v in values.items() if k != 'password'}))
        else:
            user = env['res.users'].create(self.vals('res.users', values))
        return user

    def b02_users(self):
        for login, name, xmlids in USERS:
            self._make_user(login, name, xmlids)
            self.log(f'User {login} / {USER_PASSWORD} - {name}')
        self.log('Ghi chú: thêm quyền Invoicing (account.group_account_invoice) để NV mua/bán/quản lý tạo được hóa đơn.')
        # "Đăng nhập thử từng user": kiểm tra quyền thật bằng cách chạy dưới quyền từng user
        checks = [
            ('nv.muahang', 'purchase.order', 'create', True), ('nv.muahang', 'sale.order', 'create', False),
            ('nv.banhang', 'sale.order', 'create', True), ('nv.banhang', 'purchase.order', 'create', False),
            ('thukho', 'stock.picking', 'write', True), ('thukho', 'purchase.order', 'create', False),
            ('quanly', 'purchase.order', 'create', True), ('quanly', 'sale.order', 'create', True),
            ('quanly', 'stock.picking', 'create', True),
        ]
        for login, model, operation, expected in checks:
            user = self.env['res.users'].search([('login', '=', login)], limit=1)
            actual = self._can(user, model, operation)
            self.log(f"{'✔' if actual == expected else '✖'} {login} {operation} {model}: "
                     f"{'được' if actual else 'không được'} (mong đợi: {'được' if expected else 'không'})")

    def _can(self, user, model, operation):
        recordset = self.env[model].with_user(user)
        if hasattr(recordset, 'has_access'):
            return recordset.has_access(operation)
        return recordset.check_access_rights(operation, raise_exception=False)

    # ================================================================ B0.3
    def b03_settings(self):
        env = self.env
        group_user = self.ref('base.group_user')
        for xmlid, label in FEATURE_GROUPS:
            group = self.ref(xmlid)
            if not group:
                self.log(f'⚠ Không có nhóm {xmlid} ở phiên bản này ({label}) - bỏ qua')
                continue
            group_user.write({'implied_ids': [Command.link(group.id)]})
            self.log(f'Bật: {label}')

        Tax = env['account.tax']
        company = self.company
        self.cache['taxes'] = {}
        for amount in (8, 10):
            for use, label in (('sale', 'Bán hàng'), ('purchase', 'Mua hàng')):
                domain = [('amount', '=', amount), ('type_tax_use', '=', use), ('amount_type', '=', 'percent'),
                          ('company_id', '=', company.id)]
                tax = Tax.search(domain, limit=1)
                if not tax:
                    tax = Tax.create(self.vals('account.tax', {
                        'name': f'GTGT {amount}% ({label})', 'amount': amount, 'amount_type': 'percent',
                        'type_tax_use': use, 'company_id': company.id, 'description': f'{amount}%'}))
                    self.log(f'Tạo thuế: {tax.name}')
                else:
                    self.log(f'Dùng thuế có sẵn: {tax.name} ({amount}% {use})')
                self.cache['taxes'][(amount, use)] = tax.id
        for field, key in (('account_sale_tax_id', (10, 'sale')), ('account_purchase_tax_id', (10, 'purchase'))):
            if field in company._fields:
                company[field] = self.cache['taxes'][key]

    def _tax_ids(self):
        if 'taxes' not in self.cache:
            self.cache['taxes'] = {}
            for amount in (8, 10):
                for use in ('sale', 'purchase'):
                    tax = self.env['account.tax'].search([('amount', '=', amount), ('type_tax_use', '=', use),
                                                          ('company_id', '=', self.company.id)], limit=1)
                    if tax:
                        self.cache['taxes'][(amount, use)] = tax.id
        return self.cache['taxes']

    # ================================================================ B1.1
    def _categ(self, name, parent):
        return self.get_or_create('product.category', [('name', '=', name), ('parent_id', '=', parent.id)],
                                  {'name': name, 'parent_id': parent.id})

    def b11_categories(self):
        root = self.ref('product.product_category_all') or self.env['product.category'].search([], limit=1)
        electronics = self._categ('Thiết bị điện tử', root)
        printer = self._categ('Máy in', electronics)
        laptop = self._categ('Laptop', electronics)
        office = self._categ('Văn phòng phẩm', root)
        self._categ('Nội thất', root)
        self.log('Cây danh mục: Thiết bị điện tử (Máy in, Laptop) · Văn phòng phẩm · Nội thất')
        for categ, method in ((electronics, 'fifo'), (printer, 'fifo'), (laptop, 'fifo'), (office, 'average')):
            if 'property_cost_method' not in categ._fields:
                self.log('⚠ Không có property_cost_method ở phiên bản này')
                break
            categ.property_cost_method = method
            self.log(f'Giá vốn {categ.complete_name}: {"FIFO" if method == "fifo" else "AVCO (bình quân)"}')
        self._try_automated_valuation([electronics, printer, laptop, office])

    def _try_automated_valuation(self, categories):
        """Bật định giá tự động (sinh bút toán kho) nếu tài khoản kho đã có; không thì để thủ công."""
        if 'property_valuation' not in self.env['product.category']._fields:
            return
        needed = [f for f in ('property_stock_valuation_account_id', 'property_stock_account_input_categ_id',
                              'property_stock_account_output_categ_id', 'property_stock_journal')
                  if f in self.env['product.category']._fields]
        for categ in categories:
            previous = categ.property_valuation
            categ.property_valuation = 'real_time'
            missing = [f for f in needed if not categ[f]]
            if missing:
                categ.property_valuation = previous or 'manual_periodic'
                self.log(f'⚠ {categ.complete_name}: thiếu tài khoản kho ({", ".join(missing)}) → giữ định giá thủ công')
            else:
                self.log(f'Định giá tự động (real-time) cho {categ.complete_name}')

    # ================================================================ B1.2
    def _uom(self, name, base=None, ratio=1.0):
        Uom = self.env['uom.uom']
        found = Uom.search([('name', '=', name)], limit=1)
        if found:
            return found
        if 'relative_uom_id' in Uom._fields:  # Odoo 19: không còn nhóm UoM
            values = {'name': name}
            if base:
                values.update({'relative_uom_id': base.id, 'relative_factor': ratio})
            return Uom.create(self.vals('uom.uom', values))
        categ = self.get_or_create('uom.category', [('name', '=', f'Nhóm {name}')], {})
        if base:
            categ = base.category_id
            values = {'name': name, 'category_id': categ.id, 'uom_type': 'bigger', 'factor_inv': ratio}
        else:
            values = {'name': name, 'category_id': categ.id, 'uom_type': 'reference'}
        return Uom.create(self.vals('uom.uom', values))

    def _create_product(self, index, spec):
        env = self.env
        existing = env['product.template'].search([('default_code', '=', spec['code'])], limit=1)
        if existing:
            return existing
        taxes = self._tax_ids()
        values = {
            'name': spec['name'], 'default_code': spec['code'], 'list_price': spec['price'],
            'standard_price': spec.get('cost', 0), 'sale_ok': True, 'purchase_ok': not spec.get('service'),
            'image_1920': self.img(spec['name'], spec.get('color', '#1b6ca8')),
        }
        if spec.get('categ'):
            values['categ_id'] = self.env['product.category'].search([('name', '=', spec['categ'])], limit=1).id
        if spec.get('service'):
            values['type'] = 'service'
        elif 'is_storable' in env['product.template']._fields:
            values.update({'type': 'consu', 'is_storable': True})
        else:
            values['type'] = 'product'
        if spec.get('tracking') and spec['tracking'] != 'none':
            values['tracking'] = spec['tracking']
        if spec.get('invoice_policy'):
            values['invoice_policy'] = spec['invoice_policy']
        sale_tax = self.first_field('product.template', 'taxes_id', 'sale_tax_ids')
        purchase_tax = self.first_field('product.template', 'supplier_taxes_id', 'purchase_tax_ids')
        if sale_tax and (10, 'sale') in taxes:
            values[sale_tax] = [Command.set([taxes[(10, 'sale')]])]
        if purchase_tax and (10, 'purchase') in taxes:
            values[purchase_tax] = [Command.set([taxes[(10, 'purchase')]])]
        if spec.get('uom'):
            base = self._uom(spec['uom'])
            values['uom_id'] = base.id
            po_name, _base_name, ratio = spec['po_uom']
            po_uom = self._uom(po_name, base, ratio)
            if 'uom_po_id' in env['product.template']._fields:
                values['uom_po_id'] = po_uom.id
            else:
                self.log(f"⚠ {spec['code']}: phiên bản này không có 'UoM mua' riêng - chọn {po_name} trực tiếp trên dòng PO")
        if spec.get('variants'):
            attr = self.get_or_create('product.attribute', [('name', '=', 'Màu sắc')], {'create_variant': 'always'})
            value_ids = [self.get_or_create('product.attribute.value',
                                            [('name', '=', n), ('attribute_id', '=', attr.id)], {}).id
                         for n in ('Đen', 'Xám')]
            values['attribute_line_ids'] = [Command.create({'attribute_id': attr.id,
                                                            'value_ids': [Command.set(value_ids)]})]
        else:
            values['barcode'] = self.ean13('893' + f'{index:09d}')
        return env['product.template'].create(self.vals('product.template', values))

    def b12_products(self):
        for index, spec in enumerate(PRODUCTS, start=1):
            template = self._create_product(index, spec)
            if spec.get('variants'):
                for variant in template.product_variant_ids:
                    color = 'DEN' if 'Đen' in variant.display_name else 'XAM'
                    variant.write({'default_code': f'GHE-XOAY-{color}',
                                   'barcode': self.ean13('893' + f'{900 + (1 if color == "DEN" else 2):09d}')})
            self.log(f"SP {spec['code']}: {spec['name']} (ảnh ✔, barcode ✔, mã nội bộ ✔)")
        # Optional Products: laptop gợi ý chuột + túi
        laptop = self.prod('LAPTOP-DELL').product_tmpl_id
        if 'optional_product_ids' in laptop._fields:
            laptop.optional_product_ids = [Command.set([self.prod('CHUOT-LOGI').product_tmpl_id.id,
                                                        self.prod('TUI-LAPTOP').product_tmpl_id.id])]
            self.log('Optional Products của Laptop: Chuột Logitech + Túi laptop')
        # Kiểm soát hóa đơn mua theo số lượng nhận cho máy in (dùng ở B3.5)
        printer = self.prod('MAY-IN-CANON').product_tmpl_id
        if 'purchase_method' in printer._fields:
            printer.purchase_method = 'receive'
            self.log('Máy in Canon: kiểm soát hóa đơn mua theo SỐ LƯỢNG NHẬN (cho bài B3.5)')

    # ================================================================ B1.3
    def _make_term(self, name, lines):
        """Tạo điều khoản thanh toán; nếu schema dòng khác phiên bản thì tạo bản rút gọn + cảnh báo."""
        Term = self.env['account.payment.term']
        term = Term.search([('name', '=', name)], limit=1)
        if term:
            return term
        try:
            with self.env.cr.savepoint():
                return Term.create({'name': name, 'line_ids': [
                    Command.create(self.vals('account.payment.term.line', line)) for line in lines]})
        except Exception as exc:  # noqa: BLE001
            self.log(f'⚠ Không tạo được dòng điều khoản "{name}" ({exc}) → tạo điều khoản rỗng, hãy chỉnh tay.')
            return Term.create({'name': name})

    def _payment_terms(self):
        Term = self.env['account.payment.term']
        immediate = self.ref('account.account_payment_term_immediate') or Term.search(
            [('name', 'ilike', 'immediate')], limit=1) or Term.create({'name': 'Thanh toán ngay'})
        d30 = self.ref('account.account_payment_term_30days') or self._make_term(
            '30 ngày', [{'value': 'percent', 'value_amount': 100.0, 'nb_days': 30}])
        split = self._make_term('50% trước, 50% sau 30 ngày', [
            {'value': 'percent', 'value_amount': 50.0, 'nb_days': 0},
            {'value': 'balance', 'nb_days': 30}])
        return {'immediate': immediate, 'd30': d30, 'split': split}

    def b13_partners(self):
        env = self.env
        terms = self._payment_terms()
        vn = self.ref('base.vn')
        for spec in VENDORS:
            country = self.ref(spec['country']) if spec.get('country') else vn
            values = {'name': spec['name'], 'ref': spec['ref'], 'is_company': True, 'company_type': 'company',
                      'city': spec['city'], 'country_id': country.id, 'supplier_rank': 1,
                      'email': f"{spec['ref'].lower()}@example.vn", 'phone': '+84 28 3888 0000',
                      'property_supplier_payment_term_id': terms[spec['term']].id}
            if spec.get('currency'):
                values['property_purchase_currency_id'] = self.currency(spec['currency']).id
            partner = self.get_or_create('res.partner', [('ref', '=', spec['ref'])], self.vals('res.partner', values))
            self.log(f"NCC {spec['ref']}: {partner.name} · {spec.get('currency', 'VND')} · {terms[spec['term']].name}")
        for spec in CUSTOMERS:
            values = {'name': spec['name'], 'ref': spec['ref'], 'is_company': True, 'company_type': 'company',
                      'city': spec['city'], 'country_id': vn.id, 'customer_rank': 1,
                      'email': f"{spec['ref'].lower()}@example.vn", 'phone': '+84 24 3777 0000',
                      'property_payment_term_id': terms[spec['term']].id}
            if spec.get('holding'):
                holding = self.get_or_create('res.partner', [('name', '=', spec['holding']), ('is_company', '=', True)],
                                             {'is_company': True, 'company_type': 'company'})
                values['parent_id'] = holding.id
            partner = self.get_or_create('res.partner', [('ref', '=', spec['ref'])], self.vals('res.partner', values))
            for contact_name, contact_type in spec['contacts']:
                self.get_or_create('res.partner', [('name', '=', contact_name), ('parent_id', '=', partner.id)], {
                    'type': contact_type, 'email': f"{self.fold(contact_name).lower().replace(' ', '.')}@example.vn"})
            self.log(f"KH {spec['ref']}: {partner.name} ({spec['city']}) · {terms[spec['term']].name}"
                     f"{' · công ty mẹ ' + spec['holding'] if spec.get('holding') else ''}")
        self._add_sellers()

    def _add_sellers(self):
        """Khai báo NCC kèm giá + lead time trên từng sản phẩm."""
        for ref, items in SELLERS.items():
            vendor = self.partner(ref)
            currency = self.currency('USD') if ref == 'NCC003' else self.company.currency_id
            for code, price, delay in items:
                template = self.prod(code).product_tmpl_id
                if template.seller_ids.filtered(lambda s: s.partner_id == vendor):
                    continue
                template.seller_ids = [Command.create(self.vals('product.supplierinfo', {
                    'partner_id': vendor.id, 'price': price, 'delay': delay, 'min_qty': 1.0,
                    'currency_id': currency.id}))]
        self.log('Đã khai báo NCC + giá mua + lead time cho các sản phẩm (NCC003 giá USD)')

    # ================================================================ B1.4
    def b14_pricelists(self):
        env = self.env
        vnd = self.currency('VND')
        Pricelist = env['product.pricelist']
        retail = self.ref('product.list0') or Pricelist.search([], limit=1)
        retail.write(self.vals('product.pricelist', {'name': 'Giá bán lẻ', 'currency_id': vnd.id}))
        self.log('Bảng giá "Giá bán lẻ": giá niêm yết')
        dealer = Pricelist.search([('name', '=', 'Giá đại lý')], limit=1)
        if not dealer:
            giay = self.prod('GIAY-A4').product_tmpl_id
            item = 'product.pricelist.item'
            dealer = Pricelist.create(self.vals('product.pricelist', {
                'name': 'Giá đại lý', 'currency_id': vnd.id,
                'item_ids': [
                    Command.create(self.vals(item, {'applied_on': '3_global', 'compute_price': 'percentage',
                                                    'percent_price': 10.0, 'min_quantity': 0})),
                    Command.create(self.vals(item, {'applied_on': '1_product', 'product_tmpl_id': giay.id,
                                                    'compute_price': 'percentage', 'percent_price': 15.0,
                                                    'min_quantity': 50})),
                ]}))
        self.log('Bảng giá "Giá đại lý": giảm 10% mọi sản phẩm; Giấy A4 mua từ 50 ram giảm 15%')
        field = self.first_field('res.partner', 'specific_property_product_pricelist', 'property_product_pricelist')
        for ref in ('KH003', 'KH004'):
            self.partner(ref).write({field: dealer.id})
            self.log(f'Gán bảng giá Đại lý cho {ref}')

    # ================================================================ B2.1
    def b21_warehouses(self):
        env = self.env
        Warehouse = env['stock.warehouse']
        main = Warehouse.search([('company_id', '=', self.company.id)], order='id', limit=1)
        hn = Warehouse.search([('code', '=', 'HN')], limit=1)
        if not hn:
            main.write({'name': 'Kho Hà Nội', 'code': 'HN'})
            hn = main
        hcm = Warehouse.search([('code', '=', 'HCM')], limit=1) or Warehouse.create(
            {'name': 'Kho Hồ Chí Minh', 'code': 'HCM', 'company_id': self.company.id})
        self.log(f'Kho: {hn.name} ({hn.code}) - kho chính · {hcm.name} ({hcm.code}) - chi nhánh')
        Location = env['stock.location']
        stock = hn.lot_stock_id
        khu_a = self.get_or_create('stock.location', [('name', '=', 'Khu A (Điện tử)'), ('location_id', '=', stock.id)],
                                   {'usage': 'internal'})
        khu_b = self.get_or_create('stock.location', [('name', '=', 'Khu B (Văn phòng phẩm)'), ('location_id', '=', stock.id)],
                                   {'usage': 'internal'})
        for shelf in ('Kệ A-01', 'Kệ A-02'):
            self.get_or_create('stock.location', [('name', '=', shelf), ('location_id', '=', khu_a.id)], {'usage': 'internal'})
        self.log('Vị trí trong Kho HN: ' + ', '.join(
            Location.search([('location_id', 'child_of', stock.id), ('id', '!=', stock.id)]).mapped('complete_name')))

    # ================================================================ B2.2
    def _count(self, product, location, qty, lot=None):
        """Điều chỉnh/nhập tồn bằng Physical Inventory (stock.quant ở inventory mode)."""
        Quant = self.env['stock.quant'].with_context(inventory_mode=True)
        values = {'product_id': product.id, 'location_id': location.id, 'inventory_quantity': qty}
        if lot:
            values['lot_id'] = lot.id
        if 'inventory_reason_id' in self.env['stock.quant']._fields:  # module intern_stock_adjust_reason
            reason = self.ref('intern_stock_adjust_reason.reason_found')
            if reason:
                values['inventory_reason_id'] = reason.id
        domain = [('product_id', '=', product.id), ('location_id', '=', location.id), ('lot_id', '=', lot.id if lot else False)]
        quant = Quant.search(domain, limit=1)
        if quant:
            quant.inventory_quantity = qty
            if 'inventory_reason_id' in values:
                quant.inventory_reason_id = values['inventory_reason_id']
        else:
            quant = Quant.create(values)
        quant.action_apply_inventory()
        return quant

    def b22_opening_stock(self):
        env = self.env
        hn = self.hn
        khu_a = env['stock.location'].search([('name', '=', 'Khu A (Điện tử)'), ('location_id', '=', hn.lot_stock_id.id)], limit=1)
        khu_b = env['stock.location'].search([('name', '=', 'Khu B (Văn phòng phẩm)'), ('location_id', '=', hn.lot_stock_id.id)], limit=1)
        ke_a01 = env['stock.location'].search([('name', '=', 'Kệ A-01')], limit=1)
        laptop, paper, pen = self.prod('LAPTOP-DELL'), self.prod('GIAY-A4'), self.prod('BUT-BI-TL')
        Lot = env['stock.lot']
        for i in range(1, 6):
            name = f'DELL5440-{i:04d}'
            lot = Lot.search([('name', '=', name), ('product_id', '=', laptop.id)], limit=1) or Lot.create(
                self.vals('stock.lot', {'name': name, 'product_id': laptop.id, 'company_id': self.company.id}))
            self._count(laptop, ke_a01 or khu_a, 1, lot)
        for name, qty in (('GIAY-LOT-001', 60), ('GIAY-LOT-002', 40)):
            lot = Lot.search([('name', '=', name), ('product_id', '=', paper.id)], limit=1) or Lot.create(
                self.vals('stock.lot', {'name': name, 'product_id': paper.id, 'company_id': self.company.id}))
            self._count(paper, khu_b, qty, lot)
        self._count(pen, khu_b, 500)
        self.log(f'Tồn đầu kỳ HN: laptop {self.onhand(laptop, hn.lot_stock_id)} (serial DELL5440-0001..0005) · '
                 f'giấy {self.onhand(paper, hn.lot_stock_id)} ram (2 lot) · bút bi {self.onhand(pen, hn.lot_stock_id)}')

    # ================================================================ B2.3
    def b23_routes(self):
        hn = self.hn
        hn.write({'reception_steps': 'two_steps', 'delivery_steps': 'pick_ship'})
        types = hn.env['stock.picking.type'].search([('warehouse_id', '=', hn.id), ('active', '=', True)])
        self.log('Kho HN: nhập 2 bước (Input → Stock), xuất 2 bước (Pick → Ship)')
        self.log('Loại chứng từ của HN: ' + ', '.join(sorted(types.mapped('name'))))
        self.log('Chứng từ sẽ sinh: Nhập = HN/IN rồi HN/INT · Xuất = HN/PICK rồi HN/OUT (xem ở B3, B4)')

    # ================================================================ B2.4
    def b24_putaway(self):
        env = self.env
        hn = self.hn
        mapping = (('Thiết bị điện tử', 'Khu A (Điện tử)'), ('Văn phòng phẩm', 'Khu B (Văn phòng phẩm)'))
        for categ_name, loc_name in mapping:
            categ = env['product.category'].search([('name', '=', categ_name)], limit=1)
            location = env['stock.location'].search([('name', '=', loc_name), ('location_id', '=', hn.lot_stock_id.id)], limit=1)
            rule = env['stock.putaway.rule'].search([('category_id', '=', categ.id), ('location_in_id', '=', hn.lot_stock_id.id)], limit=1)
            if not rule:
                env['stock.putaway.rule'].create(self.vals('stock.putaway.rule', {
                    'category_id': categ.id, 'location_in_id': hn.lot_stock_id.id, 'location_out_id': location.id}))
            self.log(f'Putaway: {categ_name} → {location.complete_name}')
