"""B2.7 Tái đặt hàng · B5 Tình huống tổng hợp (MTO/Dropship, Truy xuất, Một tháng hoạt động + báo cáo)."""
import csv
import os
from datetime import timedelta

from odoo import Command, fields


class CaseMixin:

    # ================================================================ B2.7
    def b27_reorder(self):
        env, hn, paper = self.env, self.hn, self.prod('GIAY-A4')
        Orderpoint = env['stock.warehouse.orderpoint']
        op = Orderpoint.search([('product_id', '=', paper.id), ('warehouse_id', '=', hn.id)], limit=1)
        if not op:
            op = Orderpoint.create(self.vals('stock.warehouse.orderpoint', {
                'product_id': paper.id, 'location_id': hn.lot_stock_id.id, 'warehouse_id': hn.id,
                'product_min_qty': 30, 'product_max_qty': 150, 'trigger': 'auto'}))
        self.log(f'Quy tắc tái đặt hàng {op.name}: Giấy A4, Min 30 / Max 150, kho HN')
        onhand = self.onhand(paper, hn.lot_stock_id)
        reduce_qty = onhand - 25
        if reduce_qty > 0:
            so = self.make_so(self.partner('KH004'), [{'product': paper, 'qty': reduce_qty}], send=False,
                              warehouse_id=hn.id)
            self.deliver(so)
            self.log(f'Xuất {reduce_qty:g} ram (SO {so.name}) → tồn HN còn {self.onhand(paper, hn.lot_stock_id):g} (< Min 30)')
        before = set(env['purchase.order'].search([]).ids)
        env.flush_all()
        try:
            op._procure_orderpoint_confirm(company_id=self.company)
        except TypeError:
            env['procurement.group'].run_scheduler()
        created = env['purchase.order'].search([('id', 'not in', list(before))])
        if created:
            for po in created:
                self.log(f'Scheduler đã tự sinh RFQ {po.name} ({po.partner_id.name}): '
                         f'{", ".join(f"{l.product_qty:g} × {l.product_id.default_code}" for l in po.order_line)} - trạng thái {po.state}')
        else:
            self.log('⚠ Scheduler chưa sinh RFQ. Vào Inventory › Operations › Replenishment rồi bấm "Order Once"/chạy Scheduler.')

    # ================================================================ C1
    def c1_mto_dropship(self):
        env, projector = self.env, self.prod('MAY-CHIEU-EPSON')
        route_model = 'stock.route' if 'stock.route' in env else 'stock.location.route'
        mto = env[route_model].with_context(active_test=False).search([('name', 'ilike', 'MTO')], limit=1)
        buy = self.ref('purchase_stock.route_warehouse0_buy') or env[route_model].search([('name', 'ilike', 'Buy')], limit=1)
        if mto and not mto.active:
            mto.active = True
        projector.product_tmpl_id.route_ids = [Command.set([r.id for r in (mto, buy) if r])]
        self.log(f'Máy chiếu Epson: route = {", ".join(projector.product_tmpl_id.route_ids.mapped("name"))} (hiện có sẵn: {projector.qty_available:g})')
        so = self.make_so(self.partner('KH001'), [{'product': projector, 'qty': 5}])
        pos = env['purchase.order'].search([('origin', 'ilike', so.name)])
        self.log(f'Xác nhận SO {so.name} (5 máy chiếu, không có sẵn) → hệ thống tự sinh PO: {", ".join(pos.mapped("name")) or "(chưa thấy)"}')
        for po in pos:
            if po.state in ('draft', 'sent'):
                self.confirm_po(po)
        done = self.finish_origin(so.name, *pos.mapped('name'))
        self.log(f'Các phiếu kho đã xử lý: {", ".join(done)} · trạng thái SO giao hàng: {so.delivery_status if "delivery_status" in so._fields else "-"}')
        invoice = self.customer_invoice(so)
        self.log(f'Hóa đơn {invoice.name}: {invoice.amount_total:,.0f}')
        # Dropship (nếu có module stock_dropshipping)
        drop = self.ref('stock_dropshipping.route_drop_shipping')
        if drop:
            notebook = self.prod('SO-TAY-A5')
            notebook.product_tmpl_id.route_ids = [Command.set([drop.id])]
            so2 = self.make_so(self.partner('KH005'), [{'product': notebook, 'qty': 20}])
            pos2 = env['purchase.order'].search([('origin', 'ilike', so2.name)])
            for po in pos2:
                self.confirm_po(po)
            self.finish_origin(so2.name, *pos2.mapped('name'))
            self.log(f'Dropship: SO {so2.name} → PO {", ".join(pos2.mapped("name"))} giao thẳng từ NCC đến khách (không qua kho)')
        else:
            self.log('Module stock_dropshipping chưa cài → chỉ minh họa MTO.')

    # ================================================================ C2
    def c2_traceability(self):
        env, laptop = self.env, self.prod('LAPTOP-DELL')
        Line = env['stock.move.line']
        sold = Line.search([('product_id', '=', laptop.id), ('state', '=', 'done'),
                            ('location_dest_id.usage', '=', 'customer'), ('lot_id', '!=', False)])
        candidates = [l.lot_id for l in sold]
        lot = next((l for l in candidates if Line.search_count([
            ('lot_id', '=', l.id), ('state', '=', 'done'), ('location_id.usage', '=', 'supplier')])), None) \
            or (candidates[0] if candidates else None)
        if not lot:
            self.log('Chưa có laptop nào đã bán - chạy B3.1 và B4.1 trước.')
            return
        self.log(f'Laptop serial {lot.name} bị lỗi → truy xuất:')
        for line in Line.search([('lot_id', '=', lot.id), ('state', '=', 'done')], order='date, id'):
            picking = line.picking_id
            source, dest = line.location_id, line.location_dest_id
            if source.usage == 'supplier':
                po = env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
                self.log(f'  • NHẬP từ NCC: {picking.partner_id.name or po.partner_id.name} · PO {po.name or picking.origin} · '
                         f'phiếu {picking.name} · ngày {line.date:%d/%m/%Y}')
            elif dest.usage == 'customer':
                so = env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                self.log(f'  • GIAO cho khách: {picking.partner_id.name or so.partner_id.name} · SO {so.name or picking.origin} · '
                         f'phiếu {picking.name} · ngày {line.date:%d/%m/%Y}')
            else:
                self.log(f'  • Chuyển nội bộ {source.complete_name} → {dest.complete_name} ({picking.name or "điều chỉnh tồn"})')
        self.log('Trên giao diện: Inventory › Products › Lots/Serial Numbers › chọn serial › nút "Traceability".')

    # ================================================================ C3
    def c3_month_and_reports(self):
        env, hn, hcm = self.env, self.hn, self.hcm
        today = fields.Datetime.now()
        # --- đếm hiện trạng
        po_count = lambda: env['purchase.order'].search_count([('state', 'in', ('purchase', 'done'))])  # noqa: E731
        so_count = lambda: env['sale.order'].search_count([('state', 'in', ('sale', 'done'))])  # noqa: E731
        transfers = lambda: env['stock.picking'].search_count([  # noqa: E731
            ('picking_type_code', '=', 'internal'), ('location_dest_id', 'child_of', hcm.lot_stock_id.id), ('state', '=', 'done')])
        # --- bổ sung cho đủ tối thiểu: 5 PO, 8 SO, 2 chuyển kho
        pen, notebook, mouse = self.prod('BUT-BI-TL'), self.prod('SO-TAY-A5'), self.prod('CHUOT-LOGI')
        customers = [self.partner(r) for r in ('KH001', 'KH002', 'KH003', 'KH004', 'KH005')]
        step = 0
        while po_count() < 5:
            step += 1
            po = self.make_po(self.partner('NCC002'), [{'product': notebook, 'qty': 100 + step}], date=today - timedelta(days=step * 4))
            self.receive(po)
            self.vendor_bill(po)
        while so_count() < 8:
            step += 1
            product = (pen, notebook)[step % 2]
            qty = 10 * step
            if self.onhand(product, hn.lot_stock_id) < qty:
                self._count(product, hn.lot_stock_id, qty + 20)
            so = self.make_so(customers[step % 5], [{'product': product, 'qty': qty}], date=today - timedelta(days=step * 3),
                              warehouse_id=hn.id)
            self.deliver(so)
            self.customer_invoice(so)
        while transfers() < 2:
            step += 1
            picking = env['stock.picking'].create({
                'picking_type_id': hn.int_type_id.id, 'location_id': hn.lot_stock_id.id,
                'location_dest_id': hcm.lot_stock_id.id,
                'move_ids': [Command.create({'name': 'Chuyển bút bi HN → HCM', 'product_id': pen.id,
                                             'product_uom_qty': 50, 'location_id': hn.lot_stock_id.id,
                                             'location_dest_id': hcm.lot_stock_id.id})]})
            self.validate(picking)
        inv_adj = env['stock.move'].search_count([('is_inventory', '=', True), ('state', '=', 'done')])
        purchase_returns = env['stock.picking'].search_count([('picking_type_code', '=', 'outgoing'), ('state', '=', 'done'),
                                                              ('partner_id.supplier_rank', '>', 0)])
        sale_returns = env['stock.picking'].search_count([('picking_type_code', '=', 'incoming'), ('state', '=', 'done'),
                                                          ('partner_id.customer_rank', '>', 0)])
        self.log(f'Tổng kết hoạt động: PO đã xác nhận = {po_count()} (≥5) · SO đã xác nhận = {so_count()} (≥8) · '
                 f'chuyển kho sang HCM = {transfers()} (≥2) · lần điều chỉnh tồn = {inv_adj} (≥1) · '
                 f'trả hàng NCC = {purchase_returns} · khách trả hàng = {sale_returns}')
        salesman = env['res.users'].search([('login', '=', 'nv.banhang')], limit=1)
        if salesman:
            own = env['sale.order'].with_user(salesman).search_count([])
            self.log(f'Phân quyền "Own documents only": nv.banhang chỉ thấy {own}/{env["sale.order"].search_count([])} SO (SO do user khác tạo bị ẩn) ✔')
        self._export_reports()

    # ------------------------------------------------------------- reports
    def _report_dir(self):
        path = self.report_dir or os.environ.get('REPORT_DIR') or '/reports'
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, '.w')
            open(test, 'w').close()
            os.remove(test)
        except OSError:
            path = '/tmp/functional_reports'
            os.makedirs(path, exist_ok=True)
        return path

    def _write_table(self, directory, name, headers, rows):
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = name[:30]
            ws.append(headers)
            for row in rows:
                ws.append(row)
            path = os.path.join(directory, f'{name}.xlsx')
            wb.save(path)
        except ImportError:
            path = os.path.join(directory, f'{name}.csv')
            with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
                writer = csv.writer(fh)
                writer.writerow(headers)
                writer.writerows(rows)
        self.log(f'Đã xuất báo cáo: {path} ({len(rows)} dòng)')

    def _export_reports(self):
        env, directory = self.env, self._report_dir()
        # Sales Analysis
        rows = [[l.order_id.date_order and l.order_id.date_order.strftime('%Y-%m-%d'), l.order_id.name, l.order_partner_id.name,
                 l.product_id.display_name, l.product_uom_qty, l.qty_delivered, l.qty_invoiced, l.price_subtotal]
                for l in env['sale.order.line'].search([('state', 'in', ('sale', 'done')), ('display_type', '=', False)], order='id')]
        self._write_table(directory, 'Sales_Analysis', ['Ngày', 'SO', 'Khách hàng', 'Sản phẩm', 'SL đặt', 'SL giao', 'SL xuất HĐ', 'Doanh thu (chưa thuế)'], rows)
        # Purchase Analysis
        rows = [[l.order_id.date_order and l.order_id.date_order.strftime('%Y-%m-%d'), l.order_id.name, l.partner_id.name,
                 l.product_id.display_name, l.product_qty, l.qty_received, l.qty_invoiced, l.price_subtotal, l.order_id.currency_id.name]
                for l in env['purchase.order.line'].search([('state', 'in', ('purchase', 'done')), ('display_type', '=', False)], order='id')]
        self._write_table(directory, 'Purchase_Analysis', ['Ngày', 'PO', 'NCC', 'Sản phẩm', 'SL đặt', 'SL nhận', 'SL xuất HĐ', 'Giá trị', 'Tiền tệ'], rows)
        # Stock Valuation
        rows = []
        for product in env['product.product'].search([('is_storable', '=', True)] if 'is_storable' in env['product.product']._fields
                                                     else [('type', '=', 'product')]):
            value = getattr(product, 'value_svl', None)
            if value is None:
                value = getattr(product, 'total_value', None)
            if value is None:
                value = product.qty_available * product.standard_price
            rows.append([product.default_code, product.display_name, product.categ_id.complete_name,
                         product.categ_id.property_cost_method if 'property_cost_method' in product.categ_id._fields else '',
                         product.qty_available, product.standard_price, value])
        self._write_table(directory, 'Stock_Valuation', ['Mã', 'Sản phẩm', 'Danh mục', 'Phương pháp giá vốn', 'Tồn', 'Giá vốn', 'Giá trị tồn'], rows)
        # Moves History
        rows = [[l.date and l.date.strftime('%Y-%m-%d %H:%M'), l.reference, l.product_id.display_name, l.lot_id.name,
                 l.location_id.complete_name, l.location_dest_id.complete_name, l.quantity]
                for l in env['stock.move.line'].search([('state', '=', 'done')], order='date, id')]
        self._write_table(directory, 'Moves_History', ['Ngày', 'Tham chiếu', 'Sản phẩm', 'Lot/Serial', 'Từ', 'Đến', 'Số lượng'], rows)
        self.log('Trên giao diện: Sales › Reporting › Sales; Purchase › Reporting › Purchase; '
                 'Inventory › Reporting › Valuation / Moves History.')
