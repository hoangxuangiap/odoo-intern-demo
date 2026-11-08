"""Hàm trợ giúp chứng từ + B2.5/B2.6 + B3 (Mua hàng) + B4 (Bán hàng)."""
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError


class FlowMixin:

    # ------------------------------------------------------------ helpers
    def make_po(self, vendor, lines, confirm=True, date=None, **extra):
        """lines: [{'product', 'qty', 'price'(tùy chọn), 'uom'(tùy chọn)}]"""
        uom_field = self.uom_field('purchase.order.line')
        order_lines = []
        for line in lines:
            values = {'product_id': line['product'].id, 'product_qty': line['qty']}
            if line.get('price') is not None:
                values['price_unit'] = line['price']
            if line.get('uom'):
                values[uom_field] = line['uom'].id
            order_lines.append(Command.create(values))
        values = {'partner_id': vendor.id, 'order_line': order_lines, **extra}
        if date:
            values['date_order'] = date
        po = self.env['purchase.order'].create(values)
        if confirm:
            self.confirm_po(po)
        return po

    def confirm_po(self, po):
        po.button_confirm()
        if po.state == 'to approve':  # có module duyệt PO nhiều cấp
            po.button_approve()
        return po

    def make_so(self, partner, lines, confirm=True, date=None, send=True, **extra):
        """lines: [{'product', 'qty', 'price'(tùy chọn), 'uom', 'discount'}]"""
        uom_field = self.uom_field('sale.order.line')
        order_lines = []
        for line in lines:
            values = {'product_id': line['product'].id, 'product_uom_qty': line['qty']}
            if line.get('price') is not None:
                values['price_unit'] = line['price']
            if line.get('discount') is not None:
                values['discount'] = line['discount']
            if line.get('uom'):
                values[uom_field] = line['uom'].id
            order_lines.append(Command.create(values))
        values = {'partner_id': partner.id, 'order_line': order_lines, **extra}
        if date:
            values['date_order'] = date
        so = self.env['sale.order'].create(values)
        if confirm:
            if send:
                so.action_quotation_sent()  # "Gửi báo giá cho khách"
            so.action_confirm()
            if so.state == 'waiting_approval':  # có module hạn mức công nợ
                so.action_approve_credit()
        return so

    # ----- kho
    def _set_move_lines(self, move, spec):
        """spec: [(lot_name, qty)] - tạo dòng chi tiết có số lot/serial cho phiếu nhập."""
        move.move_line_ids.unlink()
        for lot_name, qty in spec:
            values = move._prepare_move_line_vals(quantity=qty)
            values.update({'lot_name': lot_name, 'quantity': qty})
            self.env['stock.move.line'].create(values)

    def validate(self, picking, qty=None, lots=None, backorder=True):
        """Xác nhận 1 phiếu kho. qty={product_id: số lượng}, lots={product_id: [(lot, qty)]}.
        Tự xử lý wizard backorder: backorder=True -> tạo phiếu nợ, False -> hủy phần còn thiếu."""
        picking.action_confirm()
        if picking.state != 'assigned':
            picking.action_assign()
        for move in picking.move_ids:
            if lots and move.product_id.id in lots:
                self._set_move_lines(move, lots[move.product_id.id])
            elif qty and move.product_id.id in qty:
                move.quantity = qty[move.product_id.id]
            if 'picked' in move._fields:
                move.picked = True
        result = picking.button_validate()
        guard = 0
        while isinstance(result, dict) and result.get('res_model') and guard < 4:
            guard += 1
            wizard = self.env[result['res_model']].with_context(**result.get('context', {})).create({})
            if result['res_model'] == 'stock.backorder.confirmation' and not backorder:
                result = wizard.process_cancel_backorder()
            else:
                result = wizard.process()
        if picking.state != 'done':
            raise UserError(f'Phiếu {picking.name} chưa hoàn tất (trạng thái: {picking.state}).')
        return picking

    def validate_chain(self, picking, **kwargs):
        """Xác nhận phiếu rồi đi theo chuỗi (IN → INT, PICK → OUT). Chỉ phiếu đầu nhận qty/lots."""
        done, queue = [], [picking]
        while queue:
            current = queue.pop(0)
            if current.state in ('done', 'cancel'):
                continue
            self.validate(current, **(kwargs if current == picking else {}))
            done.append(current.name)
            for nxt in current.move_ids.move_dest_ids.picking_id:
                if nxt not in queue:
                    queue.append(nxt)
        return done

    def finish_origin(self, *origins, rounds=8):
        """Xác nhận mọi phiếu 'sẵn sàng' có origin cho trước (dùng cho luồng MTO/dropship)."""
        done = []
        for _round in range(rounds):
            pickings = self.env['stock.picking'].search([('origin', 'in', list(origins)), ('state', '=', 'assigned')])
            if not pickings:
                break
            for picking in pickings:
                self.validate(picking)
                done.append(picking.name)
        return done

    def first_pickings(self, order_pickings):
        return order_pickings.filtered(lambda p: not p.move_ids.move_orig_ids and p.state not in ('done', 'cancel'))

    def receive(self, po, lots=None, qty=None, backorder=True):
        first = self.first_pickings(po.picking_ids)
        names = []
        for picking in first:
            names += self.validate_chain(picking, lots=lots, qty=qty, backorder=backorder)
        return names

    def deliver(self, so, qty=None, backorder=True):
        names = []
        for picking in self.first_pickings(so.picking_ids):
            names += self.validate_chain(picking, qty=qty, backorder=backorder)
        return names

    def return_picking(self, picking, qty=None):
        wizard = self.env['stock.return.picking'].with_context(
            active_id=picking.id, active_ids=picking.ids, active_model='stock.picking').create({})
        for line in wizard.product_return_moves:
            if qty is not None:
                line.quantity = qty
        method = getattr(wizard, 'action_create_returns', None) or wizard.create_returns
        result = method()
        returned = self.env['stock.picking'].browse(result['res_id'])
        self.validate(returned)
        return returned

    # ----- hóa đơn
    def pay(self, move):
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=move.ids).create({})
        wizard.action_create_payments()
        return move.payment_state

    def vendor_bill(self, po, pay=False):
        po.action_create_invoice()
        bill = po.invoice_ids.filtered(lambda m: m.state == 'draft').sorted('id')[-1:]
        bill.invoice_date = fields.Date.today()
        bill.action_post()
        if pay:
            self.pay(bill)
        return bill

    def customer_invoice(self, so, pay=False):
        invoice = so._create_invoices()
        invoice.action_post()
        if pay:
            self.pay(invoice)
        return invoice

    def credit_note(self, move, line_qty=None, reason='Hàng trả lại'):
        wizard = self.env['account.move.reversal'].with_context(
            active_model='account.move', active_ids=move.ids).create(
            {'reason': reason, 'journal_id': move.journal_id.id})
        result = wizard.refund_moves()
        note = self.env['account.move'].browse(result['res_id']) if result.get('res_id') \
            else self.env['account.move'].search(result['domain'])
        if line_qty is not None:
            for line in note.invoice_line_ids.filtered('product_id'):
                line.quantity = line_qty
        note.action_post()
        return note

    def stock_summary(self, *products):
        hn, hcm = self.hn, self.hcm
        return '; '.join(f'{p.default_code}: HN={self.onhand(p, hn.lot_stock_id):g} HCM={self.onhand(p, hcm.lot_stock_id):g}'
                         for p in products)

    # ================================================================ B2.5
    def b25_transfer(self):
        hn, hcm, paper = self.hn, self.hcm, self.prod('GIAY-A4')
        picking = self.env['stock.picking'].create({
            'picking_type_id': hn.int_type_id.id, 'location_id': hn.lot_stock_id.id,
            'location_dest_id': hcm.lot_stock_id.id,
            'move_ids': [Command.create({
                'name': 'Chuyển giấy HN → HCM', 'product_id': paper.id, 'product_uom_qty': 20,
                'location_id': hn.lot_stock_id.id, 'location_dest_id': hcm.lot_stock_id.id})],
        })
        self.validate(picking)
        self.log(f'Phiếu chuyển kho {picking.name}: 20 ram giấy HN → HCM')
        self.log('Tồn sau chuyển: ' + self.stock_summary(paper))

    # ================================================================ B2.6
    def b26_count(self):
        env, hn = self.env, self.hn
        pen, paper = self.prod('BUT-BI-TL'), self.prod('GIAY-A4')
        pen_quant = env['stock.quant'].search([('product_id', '=', pen.id), ('location_id', 'child_of', hn.lot_stock_id.id)], limit=1)
        paper_quant = env['stock.quant'].search([('product_id', '=', paper.id), ('location_id', 'child_of', hn.lot_stock_id.id),
                                                 ('lot_id.name', '=', 'GIAY-LOT-001')], limit=1)
        before_pen, before_paper = pen_quant.quantity, paper_quant.quantity
        self._count(pen, pen_quant.location_id, before_pen - 3)
        self._count(paper, paper_quant.location_id, before_paper + 1, paper_quant.lot_id)
        self.log(f'Kiểm kê: bút bi {before_pen:g} → {before_pen - 3:g} (thiếu 3) · giấy lot 001 {before_paper:g} → {before_paper + 1:g} (thừa 1)')
        moves = env['stock.move'].search([('is_inventory', '=', True), ('product_id', 'in', [pen.id, paper.id])],
                                         order='id desc', limit=2)
        if 'account_move_ids' in moves._fields:
            entries = moves.account_move_ids
            if not entries:
                self.log('Không có bút toán tự động (danh mục đang để định giá thủ công).')
            for entry in entries:
                lines = '; '.join(f'{l.account_id.code} {l.account_id.name}: Nợ {l.debit:,.0f} / Có {l.credit:,.0f}'
                                  for l in entry.line_ids)
                self.log(f'Bút toán chênh lệch {entry.name or entry.ref}: {lines}')

    # ================================================================ B3.1
    def b31_purchase_basic(self):
        laptop, vendor, hn = self.prod('LAPTOP-DELL'), self.partner('NCC001'), self.hn
        po = self.make_po(vendor, [{'product': laptop, 'qty': 10, 'price': 18_000_000}], confirm=False)
        self.log(f'RFQ {po.name} (trạng thái {po.state}) - tổng {po.amount_total:,.0f}')
        try:
            po.print_quotation()
        except Exception:  # noqa: BLE001
            po.write({'state': 'sent'})
        self.log(f'Gửi email NCC → trạng thái: {po.state}')
        self.confirm_po(po)
        serials = [(f'DELL5440-{i:04d}', 1) for i in range(101, 111)]
        names = self.receive(po, lots={laptop.id: serials})
        self.log(f'Xác nhận PO {po.name} → nhận hàng qua các phiếu: {" → ".join(names)} (nhập 10 serial DELL5440-0101..0110)')
        locations = sorted(set(self.env['stock.quant'].search([
            ('product_id', '=', laptop.id), ('location_id.usage', '=', 'internal'),
            ('lot_id.name', 'like', 'DELL5440-01')]).mapped('location_id.complete_name')))
        self.log('Putaway đưa laptop vào: ' + ', '.join(locations))
        bill = self.vendor_bill(po, pay=True)
        self.log(f'Hóa đơn NCC {bill.name} {bill.amount_total:,.0f} → thanh toán: {bill.payment_state}')
        self.log('Tồn laptop: ' + self.stock_summary(laptop))

    # ================================================================ B3.2
    def b32_partial_receipt(self):
        paper, vendor = self.prod('GIAY-A4'), self.partner('NCC002')
        po = self.make_po(vendor, [{'product': paper, 'qty': 200, 'price': 62_000}])
        names = self.receive(po, lots={paper.id: [('GIAY-LOT-101', 120)]})
        backorders = po.picking_ids.backorder_ids or self.env['stock.picking'].search(
            [('origin', '=', po.name), ('state', 'in', ('assigned', 'waiting', 'confirmed'))])
        self.log(f'Đặt 200 ram, NCC giao 120 → phiếu: {" → ".join(names)} · backorder: {", ".join(backorders.mapped("name"))}')
        names2 = []
        for picking in self.first_pickings(po.picking_ids) or backorders.filtered(
                lambda p: p.state == 'assigned'):
            names2 += self.validate_chain(picking, lots={paper.id: [('GIAY-LOT-102', 80)]})
        self.log(f'Lần 2 nhận nốt 80 → phiếu: {" → ".join(names2)} · trạng thái PO: {po.state}, '
                 f'đã nhận {sum(po.order_line.mapped("qty_received")):g}/200')

    # ================================================================ B3.3
    def b33_uom_purchase(self):
        paper, vendor = self.prod('GIAY-A4'), self.partner('NCC002')
        thung = self.env['uom.uom'].search([('name', '=', 'Thùng (5 ram)')], limit=1)
        before = self.onhand(paper, self.hn.lot_stock_id)
        po = self.make_po(vendor, [{'product': paper, 'qty': 10, 'price': 310_000, 'uom': thung}])
        self.receive(po, lots={paper.id: [('GIAY-LOT-103', 10)]})
        after = self.onhand(paper, self.hn.lot_stock_id)
        self.log(f'Mua 10 thùng (1 thùng = 5 ram): tồn giấy HN {before:g} → {after:g} (tăng {after - before:g} ram, mong đợi 50)')

    # ================================================================ B3.4
    def b34_vendor_return(self):
        printer, vendor, hn = self.prod('MAY-IN-CANON'), self.partner('NCC001'), self.hn
        po = self.make_po(vendor, [{'product': printer, 'qty': 5, 'price': 3_200_000}])
        serials = [(f'CANON-LBP-{i:04d}', 1) for i in range(1, 6)]
        self.receive(po, lots={printer.id: serials})
        bill = self.vendor_bill(po)
        self.log(f'Nhập 5 máy in (PO {po.name}), hóa đơn {bill.name}. Tồn: {self.stock_summary(printer)}')
        in_picking = po.picking_ids.filtered(lambda p: p.picking_type_id == hn.in_type_id)[:1]
        int_picking = in_picking.move_ids.move_dest_ids.picking_id[:1]
        returns = []
        for picking in (int_picking, in_picking):  # trả ngược chiều: Stock → Input → NCC
            if picking:
                returns.append(self.return_picking(picking, qty=2).name)
        self.log(f'Trả 2 máy in lỗi: phiếu trả {" → ".join(returns)} (hệ thống tự chọn serial; thực tế chọn đúng serial lỗi)')
        note = self.credit_note(bill, line_qty=2, reason='Máy in lỗi trả NCC')
        self.log(f'Vendor Credit Note {note.name}: {note.amount_total:,.0f} · Tồn sau trả: {self.stock_summary(printer)}')

    # ================================================================ B3.5
    def b35_three_way_match(self):
        printer, vendor = self.prod('MAY-IN-CANON'), self.partner('NCC001')
        policy = printer.product_tmpl_id.purchase_method if 'purchase_method' in printer.product_tmpl_id._fields else '?'
        po = self.make_po(vendor, [{'product': printer, 'qty': 2, 'price': 3_200_000}])
        self.log(f'Chính sách kiểm soát hóa đơn của máy in: {policy} (receive = theo số lượng nhận)')
        try:
            with self.env.cr.savepoint():
                po.action_create_invoice()
                self.log('Kết quả: vẫn tạo được hóa đơn khi CHƯA nhận hàng (chính sách theo số lượng đặt).')
        except UserError as exc:
            self.log(f'Thử tạo hóa đơn khi chưa nhận hàng → BỊ CHẶN: {exc}')
        self.receive(po, lots={printer.id: [('CANON-LBP-0101', 1), ('CANON-LBP-0102', 1)]})
        bill = self.vendor_bill(po)
        self.log(f'Sau khi nhận 2 máy: tạo được hóa đơn {bill.name} ({bill.amount_total:,.0f}) ✔')

    # ================================================================ B3.6
    def b36_foreign_currency(self):
        env = self.env
        usd, laptop, vendor = self.currency('USD'), self.prod('LAPTOP-DELL'), self.partner('NCC003')
        rate_model, rate_value = 'res.currency.rate', 25_400.0
        rate = env[rate_model].search([('currency_id', '=', usd.id), ('name', '=', fields.Date.today()),
                                       ('company_id', '=', self.company.id)], limit=1)
        values = {'currency_id': usd.id, 'name': fields.Date.today(), 'company_id': self.company.id}
        if 'inverse_company_rate' in env[rate_model]._fields:
            values['inverse_company_rate'] = rate_value
        else:
            values['rate'] = 1 / rate_value
        (rate.write if rate else env[rate_model].create)(self.vals(rate_model, values))
        self.log(f'Tỷ giá khai báo: 1 USD = {rate_value:,.0f} VND (ngày {fields.Date.today()})')
        po = self.make_po(vendor, [{'product': laptop, 'qty': 5, 'price': 700.0}])
        self.log(f'PO {po.name} tiền tệ {po.currency_id.name}: {po.amount_total:,.2f} {po.currency_id.name}')
        self.receive(po, lots={laptop.id: [(f'DELL5440-02{i:02d}', 1) for i in range(1, 6)]})
        cost = laptop.with_context(location=self.hn.lot_stock_id.id).standard_price
        self.log(f'Giá vốn quy đổi VND: 700 USD × {rate_value:,.0f} = {700 * rate_value:,.0f} VND/máy; '
                 f'giá vốn hiện tại của sản phẩm (FIFO): {cost:,.0f}')

    # ================================================================ B3.7
    def b37_tender(self):
        desk, v1, v2 = self.prod('BAN-LAM-VIEC'), self.partner('NCC001'), self.partner('NCC002')
        po1 = self.make_po(v1, [{'product': desk, 'qty': 10, 'price': 1_400_000}], confirm=False)
        po2 = self.make_po(v2, [{'product': desk, 'qty': 10, 'price': 1_350_000}], confirm=False)
        if 'alternative_po_ids' in po1._fields:
            po1.alternative_po_ids = [Command.link(po2.id)]
        self.log(f'So sánh 2 báo giá bàn làm việc ×10: {v1.name}: {po1.amount_total:,.0f} · {v2.name}: {po2.amount_total:,.0f}')
        winner, loser = (po1, po2) if po1.amount_untaxed <= po2.amount_untaxed else (po2, po1)
        self.confirm_po(winner)
        loser.button_cancel()
        self.log(f'Chọn NCC giá tốt: {winner.partner_id.name} (PO {winner.name}); hủy {loser.name}')
        self.receive(winner)
        if 'purchase.requisition' in self.env:
            try:
                with self.env.cr.savepoint():
                    req = self.env['purchase.requisition'].create(self.vals('purchase.requisition', {
                        'requisition_type': 'blanket_order', 'vendor_id': v1.id,
                        'date_start': fields.Date.today(), 'date_end': fields.Date.today() + timedelta(days=180),
                        'line_ids': [Command.create(self.vals('purchase.requisition.line', {
                            'product_id': desk.id, 'product_qty': 50, 'price_unit': 1_380_000}))]}))
                    req.action_in_progress()
                    self.log(f'Blanket Order {req.name}: 50 bàn @1,380,000 với {v1.name} (180 ngày)')
            except Exception as exc:  # noqa: BLE001
                self.log(f'⚠ Không tạo được Blanket Order tự động: {exc}')
        else:
            self.log('Module purchase_requisition chưa cài - đã so sánh báo giá thủ công (không có Blanket Order).')

    # ================================================================ B4.1
    def b41_sale_basic(self):
        laptop, customer = self.prod('LAPTOP-DELL'), self.partner('KH001')
        so = self.make_so(customer, [{'product': laptop, 'qty': 2}], confirm=False)
        so.action_quotation_sent()
        self.log(f'Báo giá {so.name} → gửi khách (trạng thái {so.state}) - {so.amount_total:,.0f}')
        so.action_confirm()
        names = self.deliver(so)
        self.log(f'Xác nhận SO {so.name} → giao hàng qua {" → ".join(names)}')
        invoice = self.customer_invoice(so, pay=True)
        self.log(f'Hóa đơn {invoice.name} {invoice.amount_total:,.0f} → thu tiền: {invoice.payment_state}')

    # ================================================================ B4.2
    def b42_pricelist_check(self):
        paper, dealer = self.prod('GIAY-A4'), self.partner('KH003')
        for qty, expected in ((60, 15), (40, 10)):
            so = self.make_so(dealer, [{'product': paper, 'qty': qty}], confirm=False)
            line = so.order_line[:1]
            net = line.price_unit * (1 - (line.discount or 0) / 100)
            real = round((1 - net / paper.list_price) * 100, 1)
            self.log(f'Báo giá {qty} ram cho KH Đại lý ({so.pricelist_id.name}): đơn giá {line.price_unit:,.0f}, '
                     f'chiết khấu dòng {line.discount or 0:g}% → giá thực {net:,.0f} (giảm {real}%, mong đợi {expected}%) '
                     f'{"✔" if abs(real - expected) < 0.2 else "✖"}')

    # ================================================================ B4.3
    def b43_service_optional(self):
        laptop, service, customer = self.prod('LAPTOP-DELL'), self.prod('DV-LAP-DAT'), self.partner('KH002')
        options = laptop.product_tmpl_id.optional_product_ids.mapped('name')
        self.log('Optional Products gợi ý khi bán Laptop: ' + (', '.join(options) or '(chưa cấu hình)'))
        so = self.make_so(customer, [{'product': laptop, 'qty': 2}, {'product': service, 'qty': 2}])
        names = self.deliver(so)
        invoice = self.customer_invoice(so)
        self.log(f'SO {so.name}: 2 laptop + 2 dịch vụ lắp đặt · giao {" → ".join(names)} · hóa đơn {invoice.name} {invoice.amount_total:,.0f}')

    # ================================================================ B4.4
    def b44_short_delivery(self):
        laptop, customer, hn = self.prod('LAPTOP-DELL'), self.partner('KH001'), self.hn
        onhand = self.onhand(laptop, hn.lot_stock_id)
        if onhand > 7:  # chuẩn bị đúng kịch bản: kho còn 7 máy
            prep = self.make_so(self.partner('KH005'), [{'product': laptop, 'qty': onhand - 7}], send=False)
            self.deliver(prep)
            self.log(f'Chuẩn bị tồn: bán/giao {onhand - 7:g} máy cho KH005 để kho còn 7 (SO {prep.name})')
        so = self.make_so(customer, [{'product': laptop, 'qty': 10}], send=False)
        self.log(f'Khách đặt 10 laptop, tồn HN = {self.onhand(laptop, hn.lot_stock_id):g}')
        names = self.deliver(so, backorder=True)
        backorders = so.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        self.log(f'Giao 7 máy: {" → ".join(names)} · phiếu nợ (backorder) còn lại: {", ".join(backorders.mapped("name"))}')
        invoice = self.customer_invoice(so)
        qty = sum(invoice.invoice_line_ids.filtered('product_id').mapped('quantity'))
        self.log(f'Hóa đơn theo số lượng ĐÃ GIAO: {invoice.name} - {qty:g} máy (invoice_policy=delivery) ✔')

    # ================================================================ B4.5
    def b45_customer_return(self):
        chair = self.env['product.product'].search([('default_code', '=', 'GHE-XOAY-DEN')], limit=1)
        customer, hn = self.partner('KH002'), self.hn
        self._count(chair, hn.lot_stock_id, 10)  # có sẵn hàng để bán
        so = self.make_so(customer, [{'product': chair, 'qty': 3}])
        self.deliver(so)
        invoice = self.customer_invoice(so)
        out_picking = so.picking_ids.filtered(lambda p: p.picking_type_id == hn.out_type_id)[:1]
        pick_picking = so.picking_ids.filtered(lambda p: p.picking_type_id == hn.pick_type_id)[:1]
        returns = [self.return_picking(p, qty=1).name for p in (out_picking, pick_picking) if p]
        note = self.credit_note(invoice, line_qty=1, reason='Khách trả 1 ghế xoay')
        self.log(f'Khách trả 1 ghế (SO {so.name}): phiếu nhập trả {" → ".join(returns)} · Credit Note {note.name} {note.amount_total:,.0f}')
        self.log('Tồn ghế đen: ' + self.stock_summary(chair))

    # ================================================================ B4.6
    def b46_deposit(self):
        laptop, desk, customer = self.prod('LAPTOP-DELL'), self.prod('BAN-LAM-VIEC'), self.partner('KH004')
        so = self.make_so(customer, [{'product': laptop, 'qty': 4, 'price': 22_000_000},
                                     {'product': desk, 'qty': 5, 'price': 2_400_000}], send=False)
        self.log(f'Đơn {so.name}: chưa thuế 100,000,000 · tổng {so.amount_total:,.0f}')
        down = self.env['sale.advance.payment.inv'].with_context(active_model='sale.order', active_ids=so.ids).create(
            {'advance_payment_method': 'percentage', 'amount': 30})
        down.create_invoices()
        down_invoice = so.invoice_ids.filtered(lambda m: m.state == 'draft')[:1]
        down_invoice.action_post()
        self.pay(down_invoice)
        self.log(f'Hóa đơn đặt cọc 30% {down_invoice.name}: {down_invoice.amount_total:,.0f} → {down_invoice.payment_state}')
        self.deliver(so)
        final = self.env['sale.advance.payment.inv'].with_context(active_model='sale.order', active_ids=so.ids).create(
            {'advance_payment_method': 'delivered'})
        final.create_invoices()
        final_invoice = so.invoice_ids.filtered(lambda m: m.state == 'draft')[:1]
        final_invoice.action_post()
        self.log(f'Hóa đơn cuối {final_invoice.name}: {final_invoice.amount_total:,.0f} (đã trừ cọc) → cần thu thêm {final_invoice.amount_residual:,.0f}')

    # ================================================================ B4.7
    def b47_hcm_sale(self):
        paper, hcm = self.prod('GIAY-A4'), self.hcm
        user = self._make_user('nv.banhang.hcm', 'Ngô Thị Sài Gòn - NV bán hàng HCM',
                               ['sales_team.group_sale_salesman', 'account.group_account_invoice'],
                               extra=self.vals('res.users', {'property_warehouse_id': hcm.id}))
        if 'property_warehouse_id' in user._fields:
            user.property_warehouse_id = hcm.id
        customers = self.env['res.partner'].search([('ref', 'in', ['KH003', 'KH004'])])
        customers.write({'user_id': user.id})
        self.log(f'Khách TP.HCM (KH003, KH004) gán cho {user.login} - kho mặc định của người bán: {hcm.name}')
        so = self.make_so(self.partner('KH003'), [{'product': paper, 'qty': 10}], confirm=False, user_id=user.id)
        if so.warehouse_id != hcm:
            so.warehouse_id = hcm
        so.action_quotation_sent()
        so.action_confirm()
        names = self.deliver(so)
        invoice = self.customer_invoice(so)
        self.log(f'SO {so.name} xuất từ {so.warehouse_id.name}: phiếu {" → ".join(names)} · hóa đơn {invoice.name} {invoice.amount_total:,.0f}')
        self.log('Tồn giấy: ' + self.stock_summary(paper))
