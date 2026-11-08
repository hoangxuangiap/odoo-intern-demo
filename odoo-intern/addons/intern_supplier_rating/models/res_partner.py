from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_rating_ids = fields.One2many('supplier.rating', 'partner_id', string="Supplier Ratings")
    rating_avg = fields.Float(string="Average Rating", compute='_compute_rating_stats', digits=(3, 2))
    rating_count = fields.Integer(string="Rating Count", compute='_compute_rating_stats')

    @api.depends('supplier_rating_ids.average_score')
    def _compute_rating_stats(self):
        # 1 câu truy vấn gom nhóm cho cả danh sách đối tác (tránh N+1 query)
        stats = {}
        if self.ids:
            groups = self.env['supplier.rating']._read_group(
                [('partner_id', 'in', self.ids)],
                ['partner_id'],
                ['average_score:avg', '__count'],
            )
            stats = {partner.id: (avg, count) for partner, avg, count in groups}
        for partner in self:
            avg, count = stats.get(partner.id, (0.0, 0))
            partner.rating_avg = avg or 0.0
            partner.rating_count = count

    def action_view_supplier_ratings(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'intern_supplier_rating.action_supplier_rating')
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action
