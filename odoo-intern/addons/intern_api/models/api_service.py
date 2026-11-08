from odoo import Command, api, models
from odoo.exceptions import UserError


class InternApiService(models.AbstractModel):
    """Logic nghiệp vụ của API nằm ở đây (controller chỉ xác thực + gọi) -> dễ viết unit test."""
    _name = 'intern.api.service'
    _description = 'Intern API Service'

    @api.model
    def get_stock(self, default_code, warehouse_code=None):
        product = self.env['product.product'].search([('default_code', '=', default_code)], limit=1)
        if not product:
            raise UserError(self.env._("Product with code '%s' not found.", default_code))
        domain = [('code', '=', warehouse_code)] if warehouse_code else []
        warehouses = self.env['stock.warehouse'].search(domain)
        if warehouse_code and not warehouses:
            raise UserError(self.env._("Warehouse '%s' not found.", warehouse_code))
        stock = []
        for warehouse in warehouses:
            scoped = product.with_context(location=warehouse.lot_stock_id.id)
            stock.append({
                'warehouse': warehouse.code,
                'on_hand': scoped.qty_available,
                'forecast': scoped.virtual_available,
                'available': scoped.free_qty,
            })
        return {'product': product.display_name, 'default_code': default_code, 'stock': stock}

    @api.model
    def create_sale_order(self, partner_ref=None, partner_id=None, lines=None, external_ref=None, confirm=False):
        Partner = self.env['res.partner']
        partner = Partner.browse(partner_id).exists() if partner_id else \
            Partner.search([('ref', '=', partner_ref)], limit=1)
        if not partner:
            raise UserError(self.env._("Customer not found."))
        if not lines:
            raise UserError(self.env._("At least one order line is required."))
        order_lines = []
        for index, line in enumerate(lines, start=1):
            product = self.env['product.product'].search([('default_code', '=', line.get('default_code'))], limit=1)
            if not product:
                raise UserError(self.env._("Line %(n)s: product '%(code)s' not found.",
                                           n=index, code=line.get('default_code')))
            qty = float(line.get('qty') or 0)
            if qty <= 0:
                raise UserError(self.env._("Line %s: quantity must be positive.", index))
            values = {'product_id': product.id, 'product_uom_qty': qty}
            if line.get('price_unit') is not None:
                values['price_unit'] = float(line['price_unit'])
            order_lines.append(Command.create(values))
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'client_order_ref': external_ref or False,
            'origin': 'API',
            'order_line': order_lines,
        })
        if confirm:
            order.action_confirm()
        return {'id': order.id, 'name': order.name, 'state': order.state, 'amount_total': order.amount_total}

    @api.model
    def get_delivery_status(self, order_name):
        order = self.env['sale.order'].search([('name', '=', order_name)], limit=1)
        if not order:
            raise UserError(self.env._("Sale order '%s' not found.", order_name))
        return {
            'order': order.name,
            'state': order.state,
            'pickings': [{
                'name': p.name,
                'state': p.state,
                'scheduled_date': p.scheduled_date and p.scheduled_date.isoformat(),
                'date_done': p.date_done and p.date_done.isoformat(),
            } for p in order.picking_ids],
        }
