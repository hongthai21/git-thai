from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Citizen(models.Model):
    _name = 'citizen'
    _description = 'citizen'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='name')

    province_id = fields.Many2one('province', string='Province')
    district_id = fields.Many2one('district', string='District')
    ward_id = fields.Many2one('ward', string='Ward')

    # === Các trường khác giữ nguyên ===
    birth_province_id = fields.Many2one('province', string="Birth Province")
    work_province_id = fields.Many2one('province', string="Work Province")
    district_domain = fields.Binary(
        compute="_compute_district_domain",
        store=False
    )

    ward_domain = fields.Binary(
        compute="_compute_ward_domain",
        store=False
    )


    # ==================== ONCHANGE ====================
    # @api.onchange('district_id')
    # def _onchange_district_id(self):
    #     if self.district_id:
    #         self.province_id = self.district_id.province_id
    #         self.ward_id = False
    #     else:
    #         self.province_id = False
    #         self.ward_id = False
    #
    # @api.onchange('ward_id')
    # def _onchange_ward_id(self):
    #     if self.ward_id:
    #         self.district_id = self.ward_id.district_id
    #         if self.district_id:
    #             self.province_id = self.district_id.province_id
    #     else:
    #         self.district_id = False
    #         self.province_id = False

    # @api.onchange('province_id')
    # def _onchange_province(self):
    #     self.district_id = False
    #     self.ward_id = False
    #
    #     if self.province_id:
    #         return {
    #             'domain': {
    #                 'district_id': [
    #                     ('province_id', '=', self.province_id.id)
    #                 ]
    #             }
    #         }
    #     else:
    #         return {
    #             'domain': {
    #                 'district_id': []
    #             }
    #         }

    @api.depends('province_id')
    def _compute_district_domain(self):
        for rec in self:
            if rec.province_id:
                rec.district_domain = [('province_id', '=', rec.province_id.id)]
            else:
                # chưa chọn tỉnh => show all
                rec.district_domain = []

    @api.depends('district_id')
    def _compute_ward_domain(self):
        for rec in self:
            if rec.district_id:
                rec.ward_domain = [('district_id', '=', rec.district_id.id)]
            else:
                # chưa chọn huyện => show all
                rec.ward_domain = []